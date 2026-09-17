"""Exchange short-lived Meta token for a 60-day Long-Lived Access Token,
or extract a Never-Expiring Page Access Token for unattended bot automations.
"""

import argparse
import sys
import httpx
from app.config import settings

GRAPH_API_VERSION = "v20.0"
BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


def check_token(token: str) -> None:
    """Inspect a token's validity and associated accounts."""
    token = token.strip()
    print("=" * 60)
    print("[*] CHECKING INSTAGRAM / META TOKEN STATUS")
    print("=" * 60)

    url = f"{BASE_URL}/me"
    try:
        res = httpx.get(url, params={"access_token": token, "fields": "id,name"})
        data = res.json()
    except Exception as e:
        print(f"[ERROR] Network error contacting Meta: {e}")
        return

    if res.status_code != 200 or "error" in data:
        err = data.get("error", {})
        code = err.get("code")
        subcode = err.get("error_subcode")
        message = err.get("message", "Unknown error")
        print(f"\n[X] TOKEN IS INVALID OR EXPIRED")
        print(f"    HTTP Status: {res.status_code}")
        print(f"    Error Code:  {code} (Subcode: {subcode})")
        print(f"    Reason:      {message}\n")
        if code == 190 and subcode == 463:
            print("(!) CAUSE: This token has expired.")
            print("    Short-lived tokens from Graph API Explorer expire in 1-2 hours.")
            print("    Follow the instructions below to generate a new token.\n")
        return

    print(f"\n[OK] TOKEN IS VALID!")
    print(f"     Account: {data.get('name')} (ID: {data.get('id')})")

    # Check connected pages and Instagram Business accounts
    accounts_url = f"{BASE_URL}/me/accounts"
    res_accounts = httpx.get(
        accounts_url,
        params={
            "access_token": token,
            "fields": "name,id,access_token,instagram_business_account{id,username}",
        },
    )
    acc_data = res_accounts.json()
    pages = acc_data.get("data", [])
    if pages:
        print(f"\n[+] FOUND {len(pages)} CONNECTED FACEBOOK PAGE(S):")
        for page in pages:
            ig_biz = page.get("instagram_business_account")
            print(f"\n  * Page: {page.get('name')} (Page ID: {page.get('id')})")
            if ig_biz:
                print(f"    - Linked Instagram ID: {ig_biz.get('id')} (@{ig_biz.get('username', 'N/A')})")
            else:
                print("    - No Instagram Business Account linked to this page.")
    print("=" * 60)


def exchange_token(short_lived_token: str) -> None:
    """Exchange short-lived token for long-lived user token and fetch permanent page token."""
    app_id = settings.meta_app_id
    app_secret = settings.meta_app_secret

    if not app_id or not app_secret:
        print("\n[ERROR] META_APP_ID and META_APP_SECRET must be set in .env")
        print("        Find them at: https://developers.facebook.com/apps/ -> App settings -> Basic")
        sys.exit(1)

    url = f"{BASE_URL}/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_lived_token.strip(),
    }

    print(f"[*] Exchanging short-lived token with Meta for App ID: {app_id}...")
    res = httpx.get(url, params=params)
    data = res.json()

    if res.status_code != 200 or "access_token" not in data:
        err = data.get("error", {})
        print(f"\n[ERROR] Error from Meta [HTTP {res.status_code}]:")
        print(f"        Message: {err.get('message')}")
        print(f"        Code: {err.get('code')}")
        if "Error validating client secret" in err.get("message", ""):
            print("\n(!) HINT: 'Error validating client secret' means META_APP_SECRET in .env is incorrect.")
            print(f"    Go to https://developers.facebook.com/apps/{app_id}/settings/basic/")
            print("    Click 'Show' under 'App secret', copy the 32-character secret, and update .env.\n")
        sys.exit(1)

    long_lived_user_token = data["access_token"]
    expires_in = data.get("expires_in", 5184000)
    days = expires_in // 86400

    print("\n" + "=" * 60)
    print("[OK] STEP 1 COMPLETE: Retrieved 60-Day Long-Lived User Token!")
    print(f"     Validity: ~{days} days")
    print("=" * 60)

    # Now attempt to get permanent Page Access Token
    accounts_url = f"{BASE_URL}/me/accounts"
    res_acc = httpx.get(
        accounts_url,
        params={
            "access_token": long_lived_user_token,
            "fields": "name,id,access_token,instagram_business_account{id,username}",
        },
    )
    acc_data = res_acc.json()
    pages = acc_data.get("data", [])

    found_permanent_token = False
    if pages:
        for page in pages:
            page_token = page.get("access_token")
            ig_biz = page.get("instagram_business_account")
            if page_token and ig_biz:
                found_permanent_token = True
                ig_id = ig_biz.get("id")
                ig_username = ig_biz.get("username", "")
                print("\n[RECOMMENDED] NEVER-EXPIRING PAGE ACCESS TOKEN FOUND!")
                print(f"  Page: {page.get('name')} | Linked IG: @{ig_username} (ID: {ig_id})")
                print("  Because this was derived from a 60-day user token, this Page Access Token NEVER EXPIRES.")
                print("  (It will keep your automated GitHub Actions bot running indefinitely without renewals!)\n")
                print(">> Copy these into your .env and GitHub Secrets (Settings -> Secrets -> Actions):")
                print("-" * 60)
                print(f"INSTAGRAM_ACCESS_TOKEN={page_token}")
                print(f"INSTAGRAM_USER_ID={ig_id}")
                print("-" * 60)
                break

    if not found_permanent_token:
        print("\n>> 60-DAY USER ACCESS TOKEN (Valid for ~60 days):")
        print("-" * 60)
        print(f"INSTAGRAM_ACCESS_TOKEN={long_lived_user_token}")
        print("-" * 60)
        print("(!) Note: Remember to renew this token every 60 days.")


def main():
    parser = argparse.ArgumentParser(description="Manage and exchange Instagram/Meta access tokens.")
    parser.add_argument("token", nargs="?", default=None, help="Short-lived token or token to check")
    parser.add_argument("--check", action="store_true", help="Check the validity and expiration of current token in .env")

    args = parser.parse_args()

    if args.check:
        token = args.token or settings.instagram_access_token
        if not token:
            print("[ERROR] No token provided and INSTAGRAM_ACCESS_TOKEN is not set in .env")
            sys.exit(1)
        check_token(token)
        return

    token = args.token or settings.instagram_access_token
    if not token:
        print("Usage: python -m scripts.get_long_lived_token <SHORT_LIVED_TOKEN>")
        print("   Or: python -m scripts.get_long_lived_token --check")
        sys.exit(1)

    exchange_token(token)


if __name__ == "__main__":
    main()

