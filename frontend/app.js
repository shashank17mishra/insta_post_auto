// StudyNotes AutoPoster - Frontend Dashboard Application

const API_BASE = '';
let currentPostPages = {}; // Cache of slide index per post

document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  loadHealthStatus();
  loadStats();
  loadTopics();
  loadDrafts();
  loadSettings();

  // Quick Generate Button
  document.getElementById('quickGenerateBtn').addEventListener('click', () => {
    generateNext();
  });

  // Refresh Buttons
  document.getElementById('refreshDraftsBtn').addEventListener('click', loadDrafts);
  document.getElementById('refreshPublishedBtn').addEventListener('click', loadPublished);

  // Filter Categories
  document.getElementById('categoryFilter').addEventListener('change', (e) => {
    loadTopics(e.target.value);
  });

  // Modal Handlers
  document.getElementById('openNewTopicModal').addEventListener('click', () => {
    openModal('newTopicModal');
  });

  document.getElementById('newTopicForm').addEventListener('submit', handleNewTopicSubmit);
  document.getElementById('saveSettingsBtn').addEventListener('click', saveSettings);
});

// Toast Notifications
function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerText = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.remove();
  }, 4000);
}

// Modal Helpers
function openModal(id) {
  document.getElementById(id).classList.add('active');
}

function closeModal(id) {
  document.getElementById(id).classList.remove('active');
}

function previewFullImage(url) {
  document.getElementById('modalImage').src = url;
  openModal('imageModal');
}

// Navigation Tabs
function initNavigation() {
  const buttons = document.querySelectorAll('.nav-btn');
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const tabId = `tab-${btn.dataset.tab}`;
      const targetPane = document.getElementById(tabId);
      if (targetPane) targetPane.classList.add('active');

      if (btn.dataset.tab === 'drafts') loadDrafts();
      if (btn.dataset.tab === 'published') loadPublished();
      if (btn.dataset.tab === 'topics') loadTopics();
      if (btn.dataset.tab === 'overview') loadStats();
    });
  });
}

// Health & Badges
async function loadHealthStatus() {
  try {
    const res = await fetch(`${API_BASE}/api/health`);
    const data = await res.json();

    const gBadge = document.getElementById('geminiBadge');
    if (data.gemini && data.gemini.configured) {
      gBadge.className = 'badge badge-green';
      gBadge.innerText = `Gemini: ${data.gemini.model}`;
    } else {
      gBadge.className = 'badge badge-amber';
      gBadge.innerText = 'Gemini: Offline Mode';
    }

    const iBadge = document.getElementById('instaBadge');
    if (data.instagram && data.instagram.publish_enabled) {
      iBadge.className = 'badge badge-green';
      iBadge.innerText = 'Meta API: Enabled';
    } else {
      iBadge.className = 'badge badge-blue';
      iBadge.innerText = 'Meta API: Disabled';
    }

    const dBadge = document.getElementById('dryRunBadge');
    if (data.instagram && data.instagram.dry_run) {
      dBadge.className = 'badge badge-amber';
      dBadge.innerText = 'Dry Run: Active';
    } else {
      dBadge.className = 'badge badge-green';
      dBadge.innerText = 'Live Mode';
    }
  } catch (e) {
    console.error('Error fetching health:', e);
  }
}

// Stats
async function loadStats() {
  try {
    const res = await fetch(`${API_BASE}/api/health`);
    const data = await res.json();
    if (data.stats) {
      document.getElementById('statTotalTopics').innerText = data.stats.total_topics || 0;
      document.getElementById('statPendingTopics').innerText = data.stats.pending_topics || 0;
      document.getElementById('statDraftPosts').innerText = data.stats.draft_posts || 0;
      document.getElementById('statApprovedPosts').innerText = data.stats.approved_posts || 0;
      document.getElementById('statPublishedPosts').innerText = data.stats.published_posts || 0;
      document.getElementById('statFailedPosts').innerText = data.stats.failed_posts || 0;
    }
  } catch (e) {
    console.error('Error fetching stats:', e);
  }
}

// Topics
async function loadTopics(category = '') {
  try {
    let url = `${API_BASE}/api/topics?limit=100`;
    if (category) url += `&category=${encodeURIComponent(category)}`;
    const res = await fetch(url);
    const data = await res.json();

    const tbody = document.getElementById('topicsTableBody');
    tbody.innerHTML = '';

    if (!data.topics || data.topics.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="text-center">No topics found.</td></tr>';
      return;
    }

    // Populate category dropdown
    loadCategories();

    data.topics.forEach(t => {
      const tr = document.createElement('tr');
      const statusClass = t.status === 'completed' ? 'badge-green' : (t.status === 'generating' ? 'badge-blue' : 'badge-amber');

      tr.innerHTML = `
        <td><strong>#${t.priority}</strong></td>
        <td><strong>${escapeHtml(t.name)}</strong></td>
        <td><span class="badge badge-gray">${escapeHtml(t.category)}</span></td>
        <td>${escapeHtml(t.difficulty)}</td>
        <td><span class="badge ${statusClass}">${t.status}</span></td>
        <td>
          <button class="btn btn-primary btn-sm" onclick="generateTopic('${t.id}')">
            ⚡ Generate
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (e) {
    console.error('Error loading topics:', e);
  }
}

async function loadCategories() {
  try {
    const res = await fetch(`${API_BASE}/api/categories`);
    const data = await res.json();
    const select = document.getElementById('categoryFilter');
    const currVal = select.value;
    select.innerHTML = '<option value="">All Categories</option>';
    data.categories.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c;
      opt.innerText = c;
      if (c === currVal) opt.selected = true;
      select.appendChild(opt);
    });
  } catch (e) {
    console.error(e);
  }
}

// Topic Creation
async function handleNewTopicSubmit(e) {
  e.preventDefault();
  const name = document.getElementById('newTopicName').value;
  const category = document.getElementById('newTopicCategory').value;
  const difficulty = document.getElementById('newTopicDifficulty').value;
  const priority = parseInt(document.getElementById('newTopicPriority').value, 10);

  try {
    const res = await fetch(`${API_BASE}/api/topics`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, category, difficulty, priority })
    });
    if (res.ok) {
      showToast('Topic added successfully!');
      closeModal('newTopicModal');
      document.getElementById('newTopicForm').reset();
      loadTopics();
      loadStats();
    } else {
      const err = await res.json();
      showToast(err.detail || 'Failed to add topic', 'error');
    }
  } catch (err) {
    showToast(`Error: ${err}`, 'error');
  }
}

// Generation Triggers
async function generateNext() {
  showToast('Generation started for next pending topic...');
  try {
    const res = await fetch(`${API_BASE}/api/generate/next`, { method: 'POST' });
    const data = await res.json();
    if (res.ok) {
      showToast(`Generated: ${data.title}!`);
      loadStats();
      loadDrafts();
    } else {
      showToast(data.detail?.message || 'Generation failed', 'error');
    }
  } catch (e) {
    showToast(`Error: ${e}`, 'error');
  }
}

async function generateTopic(topicId) {
  showToast(`Generating notes for topic...`);
  try {
    const res = await fetch(`${API_BASE}/api/generate/${topicId}`, { method: 'POST' });
    const data = await res.json();
    if (res.ok) {
      showToast(`Generated post #${data.post_id}: ${data.title}`);
      loadStats();
      loadTopics();
    } else {
      showToast(data.detail?.message || 'Generation failed', 'error');
    }
  } catch (e) {
    showToast(`Error: ${e}`, 'error');
  }
}

// Drafts & Carousel Review
async function loadDrafts() {
  const container = document.getElementById('draftsListContainer');
  try {
    const res = await fetch(`${API_BASE}/api/posts?limit=50`);
    const data = await res.json();

    container.innerHTML = '';
    const drafts = (data.posts || []).filter(p => p.status !== 'published');

    if (drafts.length === 0) {
      container.innerHTML = '<p class="text-muted">No drafts available. Click "Generate Next Topic" to create one!</p>';
      return;
    }

    drafts.forEach(post => {
      container.appendChild(renderPostCard(post, false));
    });
  } catch (e) {
    console.error('Error loading drafts:', e);
  }
}

async function loadPublished() {
  const container = document.getElementById('publishedListContainer');
  try {
    const res = await fetch(`${API_BASE}/api/posts?status=published&limit=50`);
    const data = await res.json();

    container.innerHTML = '';
    const published = data.posts || [];

    if (published.length === 0) {
      container.innerHTML = '<p class="text-muted">No published posts yet.</p>';
      return;
    }

    published.forEach(post => {
      container.appendChild(renderPostCard(post, true));
    });
  } catch (e) {
    console.error('Error loading published posts:', e);
  }
}

function renderPostCard(post, isPublished) {
  const card = document.createElement('div');
  card.className = 'post-card';
  card.id = `postCard_${post.id}`;

  const pages = post.pages || [];
  currentPostPages[post.id] = 0; // Start at slide 0

  const statusBadge = post.status === 'published' ? 'badge-green' : (post.status === 'approved' ? 'badge-purple' : 'badge-blue');

  card.innerHTML = `
    <!-- Left Column: Interactive Carousel -->
    <div class="carousel-preview">
      <div class="carousel-viewer">
        <img id="postImg_${post.id}" src="${pages.length > 0 ? '/' + pages[0].file_path : ''}" alt="Slide" onclick="previewFullImage(this.src)">
        ${pages.length > 1 ? `
          <button class="carousel-nav-btn carousel-prev" onclick="changeSlide(${post.id}, -1)">‹</button>
          <button class="carousel-nav-btn carousel-next" onclick="changeSlide(${post.id}, 1)">›</button>
        ` : ''}
      </div>
      <div class="carousel-counter" id="postCounter_${post.id}">
        Slide 1 of ${pages.length} (Click image to zoom)
      </div>
    </div>

    <!-- Right Column: Info & Actions -->
    <div class="post-info">
      <div class="post-header-row">
        <div>
          <h3>#${post.id} ${escapeHtml(post.title)}</h3>
          <div class="post-meta-tags">
            <span class="badge ${statusBadge}">${post.status.toUpperCase()}</span>
            <span class="badge badge-gray">Topic: ${escapeHtml(post.topic_id)}</span>
            ${post.dry_run ? '<span class="badge badge-amber">Dry Run</span>' : ''}
          </div>
        </div>
      </div>

      <label class="text-muted font-bold">Instagram Caption & Hashtags:</label>
      <div class="caption-box">${escapeHtml(post.caption)}</div>

      ${post.instagram_media_id ? `
        <div class="hint">
          <strong>Instagram Media ID:</strong> <code>${escapeHtml(post.instagram_media_id)}</code>
        </div>
      ` : ''}

      <div class="post-actions">
        ${!isPublished && post.status !== 'approved' ? `
          <button class="btn btn-success" onclick="approvePost(${post.id})">✓ Approve Draft</button>
        ` : ''}

        ${!isPublished ? `
          <button class="btn btn-primary" onclick="publishPost(${post.id})">🚀 Publish Now</button>
          <button class="btn btn-secondary" onclick="regeneratePost(${post.id})">🔄 Regenerate</button>
          <button class="btn btn-danger" onclick="rejectPost(${post.id})">✕ Reject</button>
        ` : ''}
      </div>
    </div>
  `;

  return card;
}

function changeSlide(postId, direction) {
  const card = document.getElementById(`postCard_${postId}`);
  if (!card) return;

  fetch(`${API_BASE}/api/posts/${postId}`)
    .then(r => r.json())
    .then(post => {
      const pages = post.pages || [];
      if (pages.length <= 1) return;

      let idx = (currentPostPages[postId] || 0) + direction;
      if (idx < 0) idx = pages.length - 1;
      if (idx >= pages.length) idx = 0;
      currentPostPages[postId] = idx;

      const img = document.getElementById(`postImg_${postId}`);
      const counter = document.getElementById(`postCounter_${postId}`);

      img.src = '/' + pages[idx].file_path;
      counter.innerText = `Slide ${idx + 1} of ${pages.length} (Click image to zoom)`;
    });
}

// Action Callbacks
async function approvePost(postId) {
  try {
    const res = await fetch(`${API_BASE}/api/posts/${postId}/approve`, { method: 'POST' });
    if (res.ok) {
      showToast(`Post #${postId} approved!`);
      loadDrafts();
      loadStats();
    } else {
      const err = await res.json();
      showToast(err.detail || 'Approval failed', 'error');
    }
  } catch (e) {
    showToast(`Error: ${e}`, 'error');
  }
}

async function rejectPost(postId) {
  if (!confirm(`Are you sure you want to reject Post #${postId}?`)) return;
  try {
    const res = await fetch(`${API_BASE}/api/posts/${postId}/reject`, { method: 'POST' });
    if (res.ok) {
      showToast(`Post #${postId} rejected.`);
      loadDrafts();
      loadStats();
    }
  } catch (e) {
    showToast(`Error: ${e}`, 'error');
  }
}

async function regeneratePost(postId) {
  showToast(`Regenerating post #${postId}...`);
  try {
    const res = await fetch(`${API_BASE}/api/posts/${postId}/regenerate`, { method: 'POST' });
    if (res.ok) {
      showToast(`Regenerated as new post!`);
      loadDrafts();
      loadStats();
    } else {
      const err = await res.json();
      showToast(err.detail?.message || 'Regeneration failed', 'error');
    }
  } catch (e) {
    showToast(`Error: ${e}`, 'error');
  }
}

async function publishPost(postId) {
  showToast(`Publishing post #${postId}...`);
  try {
    const res = await fetch(`${API_BASE}/api/posts/${postId}/publish?force=true`, { method: 'POST' });
    const data = await res.json();
    if (res.ok) {
      showToast(data.message || `Post #${postId} published successfully!`);
      loadDrafts();
      loadPublished();
      loadStats();
    } else {
      showToast(data.detail || 'Publishing failed', 'error');
    }
  } catch (e) {
    showToast(`Error: ${e}`, 'error');
  }
}

// Settings
async function loadSettings() {
  try {
    const res = await fetch(`${API_BASE}/api/settings`);
    const data = await res.json();
    const s = data.settings || {};

    document.getElementById('settingEnv').value = s.app_env || 'development';
    document.getElementById('settingModel').value = s.gemini_model || 'gemini-3.8-flash';
    document.getElementById('settingPublishEnabled').checked = Boolean(s.instagram_publish_enabled);
    document.getElementById('settingDryRun').checked = Boolean(s.dry_run);
    document.getElementById('settingCron').value = s.posting_cron || '0 12 * * *';
    document.getElementById('settingPublicUrl').value = s.public_base_url || 'http://localhost:8000';

    updateToggleLabels();
  } catch (e) {
    console.error('Error loading settings:', e);
  }
}

function updateToggleLabels() {
  const pub = document.getElementById('settingPublishEnabled').checked;
  document.getElementById('publishEnabledText').innerText = pub
    ? 'Enabled (Will publish to live Meta Graph API)'
    : 'Disabled (Draft & dry-run only)';

  const dry = document.getElementById('settingDryRun').checked;
  document.getElementById('dryRunText').innerText = dry
    ? 'Active (Simulates containers & publication)'
    : 'Inactive (Real Meta Graph API calls)';
}

document.getElementById('settingPublishEnabled').addEventListener('change', updateToggleLabels);
document.getElementById('settingDryRun').addEventListener('change', updateToggleLabels);

async function saveSettings() {
  const dry_run = document.getElementById('settingDryRun').checked;
  const publish_enabled = document.getElementById('settingPublishEnabled').checked;
  const posting_cron = document.getElementById('settingCron').value;

  try {
    const res = await fetch(`${API_BASE}/api/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dry_run, publish_enabled, posting_cron })
    });
    if (res.ok) {
      showToast('Settings saved successfully!');
      loadHealthStatus();
    } else {
      showToast('Failed to save settings', 'error');
    }
  } catch (e) {
    showToast(`Error: ${e}`, 'error');
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
