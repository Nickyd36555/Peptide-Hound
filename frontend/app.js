'use strict';

let allGroups = [];
let sortCol = 'normalized_name';
let sortDir = 1; // 1 = asc, -1 = desc

// ── Fetch products ───────────────────────────────────────────────────────
async function loadProducts() {
  setBodyState('loading', 'Loading…');
  try {
    const res = await fetch('/api/products');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    allGroups = await res.json();
    renderTable();
  } catch (err) {
    setBodyState('error', `Failed to load products: ${err.message}`);
  }
}

// ── Render table ─────────────────────────────────────────────────────────
function renderTable() {
  const query = document.getElementById('search').value.toLowerCase().trim();
  const filtered = query
    ? allGroups.filter(g => g.normalized_name.toLowerCase().includes(query))
    : allGroups;

  const sorted = [...filtered].sort((a, b) => {
    const av = a[sortCol], bv = b[sortCol];
    if (typeof av === 'string') return av.localeCompare(bv) * sortDir;
    return (av - bv) * sortDir;
  });

  const tbody = document.getElementById('products-body');
  tbody.innerHTML = '';

  if (sorted.length === 0) {
    setBodyState(
      'empty',
      query
        ? `No peptides match "${esc(query)}".`
        : 'No products yet. Click <strong>Refresh Prices</strong> to scrape vendor sites.'
    );
    return;
  }

  const fragment = document.createDocumentFragment();

  sorted.forEach((group, idx) => {
    const mainRow = document.createElement('tr');
    mainRow.className = 'main-row';
    mainRow.innerHTML = `
      <td class="col-peptide">${esc(group.normalized_name)}</td>
      <td class="col-ppm">$${fmt4(group.cheapest_price_per_mg)}/mg</td>
      <td class="col-price">$${fmt2(group.cheapest_price)}</td>
      <td class="col-vendor">${esc(group.cheapest_vendor)}</td>
      <td class="col-count"><span class="badge-count">${group.vendor_count}</span></td>
      <td><button class="expand-btn" data-idx="${idx}">View All ▾</button></td>
    `;
    fragment.appendChild(mainRow);

    const expandRow = document.createElement('tr');
    expandRow.className = 'expand-row hidden';
    expandRow.dataset.idx = idx;
    expandRow.innerHTML = `<td><div class="expand-inner">${buildVendorTable(group)}</div></td>`;
    fragment.appendChild(expandRow);
  });

  tbody.appendChild(fragment);

  // Attach expand/collapse listeners
  tbody.querySelectorAll('.expand-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const idx = btn.dataset.idx;
      const expRow = tbody.querySelector(`.expand-row[data-idx="${idx}"]`);
      if (!expRow) return;
      const open = !expRow.classList.contains('hidden');
      expRow.classList.toggle('hidden', open);
      btn.textContent = open ? 'View All ▾' : 'Collapse ▴';
    });
  });
}

function buildVendorTable(group) {
  const rows = group.listings.map((l, i) => {
    const isCheapest = i === 0;
    return `
      <tr class="${isCheapest ? 'cheapest-row' : ''}">
        <td>${esc(l.vendor)}</td>
        <td>${esc(l.name)}</td>
        <td>${l.weight_mg} mg</td>
        <td>$${fmt2(l.price)}</td>
        <td class="col-vt-ppm">$${fmt4(l.price_per_mg)}</td>
        <td><a class="vendor-link" href="${esc(l.url)}" target="_blank" rel="noopener noreferrer">Buy ↗</a></td>
      </tr>
    `;
  }).join('');

  return `
    <table class="vendor-table">
      <thead>
        <tr>
          <th>Vendor</th>
          <th>Product</th>
          <th>Weight</th>
          <th>Price</th>
          <th>$/mg</th>
          <th>Link</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

// ── Refresh / scrape ──────────────────────────────────────────────────────
async function refreshPrices() {
  const btn = document.getElementById('refresh-btn');
  const bar = document.getElementById('status-bar');

  btn.disabled = true;
  btn.innerHTML = `
    <svg viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" width="16" height="16"
         style="animation:spin .7s linear infinite">
      <path d="M4 10a6 6 0 1 1 1.5 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <polyline points="1,10 4,13 7,10" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
    </svg>
    Scraping…
  `;
  showStatus('info', 'Scraping vendor sites — this may take up to 60 seconds…');

  try {
    const res = await fetch('/api/scrape', { method: 'POST' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    const vendorSummary = data.vendors.map(v => `${v.vendor} (${v.count})`).join(', ');
    const errNote = data.errors.length
      ? ` — ${data.errors.length} vendor(s) failed: ${data.errors.map(e => e.split(':')[0]).join(', ')}`
      : '';

    showStatus(
      data.errors.length && data.scraped === 0 ? 'error' : 'success',
      `Scraped ${data.scraped} products from ${data.vendors.length} vendor(s).` +
      (vendorSummary ? ` ${vendorSummary}.` : '') + errNote
    );
    await loadProducts();
  } catch (err) {
    showStatus('error', `Scrape failed: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `
      <svg viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" width="16" height="16">
        <path d="M4 10a6 6 0 1 1 1.5 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <polyline points="1,10 4,13 7,10" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
      </svg>
      Refresh Prices
    `;
  }
}

// ── Sort headers ──────────────────────────────────────────────────────────
document.querySelectorAll('th[data-sort]').forEach(th => {
  th.addEventListener('click', () => {
    if (sortCol === th.dataset.sort) {
      sortDir *= -1;
    } else {
      sortCol = th.dataset.sort;
      sortDir = 1;
    }
    document.querySelectorAll('th[data-sort]').forEach(h => {
      h.classList.remove('sorted-asc', 'sorted-desc');
      h.querySelector('.sort-arrow').textContent = '';
    });
    th.classList.add(sortDir === 1 ? 'sorted-asc' : 'sorted-desc');
    th.querySelector('.sort-arrow').textContent = sortDir === 1 ? '↑' : '↓';
    renderTable();
  });
});

// ── Search ────────────────────────────────────────────────────────────────
document.getElementById('search').addEventListener('input', renderTable);

// ── Refresh button ────────────────────────────────────────────────────────
document.getElementById('refresh-btn').addEventListener('click', refreshPrices);

// ── Helpers ───────────────────────────────────────────────────────────────
function esc(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function fmt2(n) { return Number(n).toFixed(2); }
function fmt4(n) { return Number(n).toFixed(4); }

function setBodyState(type, html) {
  document.getElementById('products-body').innerHTML =
    `<tr><td colspan="6" class="state-cell ${type}">${html}</td></tr>`;
}

function showStatus(type, msg) {
  const bar = document.getElementById('status-bar');
  bar.className = `status-bar ${type}`;
  bar.textContent = msg;
}

// ── Init ──────────────────────────────────────────────────────────────────
loadProducts();
