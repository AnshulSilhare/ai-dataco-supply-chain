let currentTheme = localStorage.getItem('dataco-theme') || 'light';

function updateTabIndicator(btn) {
    if (!btn) return;
    const nav = btn.closest('.tab-nav') || btn.closest('.nav-tabs');
    if (!nav) return;
    const indicator = nav.querySelector('.tab-indicator');
    if (!indicator) return;
    
    indicator.style.width = `${btn.offsetWidth}px`;
    indicator.style.left = `${btn.offsetLeft}px`;
}

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Apply saved theme
    if (currentTheme === 'dark') document.body.classList.add('dark');
    
    // 2. Fetch config and populate dropdowns
    await loadConfig();
    
    // 3. Set up tab navigation
    setupTabs();
    
    // 4. Set up slider value displays
    setupSliders();
    
    // 5. Set up file upload drag-and-drop
    setupFileUpload();
    
    // 6. Load feature importance chart on architecture tab
    loadImportanceChart();
    
    // 7. Set up theme toggle
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }

    // 8. Set up Adaptive Control Capsule (DemandSense Physics)
    setupCollapsibleCapsule();
    
    // 9. Tab Indicator Resize Handler
    window.addEventListener('resize', () => {
        document.querySelectorAll('.tab-btn.active').forEach(btn => updateTabIndicator(btn));
    });
    
    // Guide Modal Logic
    const guideModal = document.getElementById('guideModal');
    if (guideModal) {
        const openGuideBtn = document.getElementById('openGuideBtn');
        const closeGuideBtn = document.getElementById('closeGuideBtn');
        if (openGuideBtn) openGuideBtn.addEventListener('click', () => guideModal.classList.add('active'));
        if (closeGuideBtn) closeGuideBtn.addEventListener('click', () => guideModal.classList.remove('active'));
        guideModal.addEventListener('click', (e) => {
            if (e.target === guideModal) guideModal.classList.remove('active');
        });

        const guideNav = document.getElementById('guideTabNav');
        setTimeout(() => { const a = guideNav ? guideNav.querySelector('.tab-btn.active') : null; if(a) updateTabIndicator(a); }, 150);

        document.querySelectorAll('#guideTabNav .tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('#guideTabNav .tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.guide-tab-pane').forEach(c => {
                    c.classList.remove('active');
                });
                
                btn.classList.add('active');
                updateTabIndicator(btn);
                
                const target = btn.getAttribute('data-guidetab');
                const targetEl = document.getElementById('guide-' + target);
                if (targetEl) {
                    targetEl.classList.add('active');
                }
            });
        });
    }

    // 10. Execute initial baseline prediction so results & prescriptive strategy are immediately visible
    setTimeout(() => {
        runPrediction(false);
    }, 250);

    // 11. Auto-collapse brand version badge after initial 2 seconds
    setTimeout(() => {
        const vBadge = document.getElementById('appVersion');
        if (vBadge) vBadge.classList.add('is-collapsed');
    }, 2000);
});

function toggleTheme() {
    document.body.classList.toggle('dark');
    currentTheme = document.body.classList.contains('dark') ? 'dark' : 'light';
    localStorage.setItem('dataco-theme', currentTheme);
    updateThemeIcon();
    refreshChartsForTheme();
}

function updateThemeIcon() {
    const btn = document.getElementById('themeToggle');
    if (btn) {
        btn.setAttribute('title', document.body.classList.contains('dark') ? 'Switch to Light Mode' : 'Switch to Dark Mode');
    }
}

function refreshChartsForTheme() {
    loadImportanceChart();
}

async function loadConfig() {
    try {
        const res = await fetch('/api/config');
        const config = await res.json();
        
        populateSelect('country', config.countries, 'United States');
        populateSelect('shippingMode', config.shipping_modes, 'Standard Class');
        populateSelect('segment', config.segments, 'Corporate');
        populateSelect('payment', config.payments, 'DEBIT');
        populateSelect('category', config.categories, 'Computers');
        populateSelect('dayOfWeek', config.days, 'Monday');
    } catch (e) {
        console.error('Failed to load config:', e);
    }
}

function populateSelect(id, options, defaultVal) {
    const el = document.getElementById(id);
    if (!el) return;
    el.innerHTML = '';
    options.forEach(opt => {
        const option = document.createElement('option');
        option.value = opt;
        option.textContent = opt;
        if (opt === defaultVal) option.selected = true;
        el.appendChild(option);
    });
}

function updateBottomNavIndicator(targetBtn) {
    const nav = document.getElementById('bottomNav') || document.querySelector('.bottom-nav');
    const indicator = document.getElementById('bnavIndicator');
    if (!nav || !indicator) return;
    
    let activeBtn = targetBtn;
    if (!activeBtn) {
        activeBtn = nav.querySelector('.bnav-btn.active') || nav.querySelector('.bnav-btn');
    }
    if (!activeBtn) return;
    
    const left = activeBtn.offsetLeft;
    const width = activeBtn.offsetWidth;
    
    if (!width || width === 0) return;
    
    indicator.style.setProperty('transform', `translate3d(${left}px, 0, 0)`, 'important');
    indicator.style.setProperty('width', `${width}px`, 'important');
    indicator.style.setProperty('opacity', '1', 'important');
    
    const blob = indicator.querySelector('.bnav-liquid-blob');
    if (blob) {
        blob.classList.remove('is-squashing');
        void blob.offsetWidth; // trigger reflow
        blob.classList.add('is-squashing');
        setTimeout(() => blob.classList.remove('is-squashing'), 400);
    }
}

function updateDesktopTabIndicator(targetBtn) {
    const nav = document.getElementById('navTabs') || document.querySelector('.nav-tabs-capsule');
    const indicator = document.getElementById('navTabIndicator');
    if (!nav || !indicator) return;
    
    let activeBtn = targetBtn;
    if (!activeBtn) {
        activeBtn = nav.querySelector('.nav-tab.active') || nav.querySelector('.nav-tab');
    }
    if (!activeBtn) return;
    
    const left = activeBtn.offsetLeft;
    const width = activeBtn.offsetWidth;
    
    if (!width || width === 0) return;
    
    indicator.style.setProperty('transform', `translate3d(${left}px, 0, 0)`, 'important');
    indicator.style.setProperty('width', `${width}px`, 'important');
    indicator.style.setProperty('opacity', '1', 'important');
    
    const blob = indicator.querySelector('.nav-tab-liquid-blob');
    if (blob) {
        blob.classList.remove('is-squashing');
        void blob.offsetWidth; // trigger reflow
        blob.classList.add('is-squashing');
        setTimeout(() => blob.classList.remove('is-squashing'), 400);
    }
}

function setupTabs() {
    const allTabs = document.querySelectorAll('.nav-tab, .tab-btn, .bnav-btn');

    allTabs.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            if (!tabId) return;
            
            // Remove active from all nav buttons
            allTabs.forEach(b => b.classList.remove('active'));
            
            // Hide all tab content panes
            document.querySelectorAll('.tab-content').forEach(p => p.classList.remove('active'));
            
            // Activate clicked buttons (sync top floating capsule and bottom nav)
            document.querySelectorAll(`[data-tab="${tabId}"]`).forEach(b => b.classList.add('active'));
            
            // Smoothly glide bottom nav liquid indicator
            const activeBnav = document.querySelector(`.bnav-btn[data-tab="${tabId}"]`);
            if (activeBnav) updateBottomNavIndicator(activeBnav);
            
            // Smoothly glide desktop top nav liquid indicator
            const activeNavTab = document.querySelector(`.nav-tab[data-tab="${tabId}"]`);
            if (activeNavTab) updateDesktopTabIndicator(activeNavTab);
            
            // Show corresponding tab pane
            const pane = document.getElementById('tab-' + tabId) || document.getElementById(tabId);
            if(pane) {
                pane.classList.add('active');
                // Smooth scroll to top of pane if on mobile
                if (window.innerWidth <= 768) {
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }
            }
            
            if(tabId === 'architecture' || tabId === 'tab-arch') loadImportanceChart();
            
            // Trigger chart resize across visible tab
            setTimeout(() => {
                document.querySelectorAll('.chart-container').forEach(c => {
                    const instance = typeof echarts !== 'undefined' ? echarts.getInstanceByDom(c) : null;
                    if (instance) instance.resize();
                });
            }, 100);
        });
    });

    window.addEventListener('resize', () => {
        updateBottomNavIndicator();
        updateDesktopTabIndicator();
    });
    window.addEventListener('orientationchange', () => {
        setTimeout(() => {
            updateBottomNavIndicator();
            updateDesktopTabIndicator();
        }, 150);
    });
    setTimeout(() => {
        const initialActiveBnav = document.querySelector('.bottom-nav .bnav-btn.active');
        if (initialActiveBnav) updateBottomNavIndicator(initialActiveBnav);
        
        const initialActiveNavTab = document.querySelector('.nav-tabs-capsule .nav-tab.active') || document.querySelector('.nav-tab.active');
        if (initialActiveNavTab) updateDesktopTabIndicator(initialActiveNavTab);
    }, 120);
}

function setupSliders() {
    const sliders = [
        { id: 'daysScheduled', displayId: 'daysScheduledValue' },
        { id: 'penaltyRate', displayId: 'penaltyRateValue' },
        { id: 'bulkPenaltyRate', displayId: 'bulkPenaltyRateValue' },
    ];
    sliders.forEach(({ id, displayId }) => {
        const slider = document.getElementById(id);
        const display = document.getElementById(displayId);
        if (slider && display) {
            slider.addEventListener('input', () => { display.textContent = slider.value; });
        }
    });
}

function setupFileUpload() {
    const area = document.getElementById('uploadArea');
    const input = document.getElementById('fileInput');
    const filenameDisplay = document.getElementById('uploadFilename');
    
    if (!area || !input || !filenameDisplay) return;

    area.addEventListener('click', () => input.click());
    
    area.addEventListener('dragover', (e) => {
        e.preventDefault();
        area.classList.add('drag-over');
    });
    area.addEventListener('dragleave', () => area.classList.remove('drag-over'));
    area.addEventListener('drop', (e) => {
        e.preventDefault();
        area.classList.remove('drag-over');
        if (e.dataTransfer.files.length) {
            input.files = e.dataTransfer.files;
            filenameDisplay.textContent = e.dataTransfer.files[0].name;
        }
    });
    
    input.addEventListener('change', () => {
        if (input.files.length) {
            filenameDisplay.textContent = input.files[0].name;
        }
    });
}

let activeScrollAnim = null;

function gracefulScrollTo(targetY, duration = 380, onComplete = null) {
    if (activeScrollAnim) {
        cancelAnimationFrame(activeScrollAnim);
        activeScrollAnim = null;
    }

    const startY = window.scrollY;
    const diff = targetY - startY;
    if (Math.abs(diff) < 4) {
        window.scrollTo({ left: 0, top: targetY, behavior: 'instant' });
        if (onComplete) onComplete();
        return;
    }
    const startTime = performance.now();

    function step(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(1, elapsed / duration);
        const ease = progress * progress * progress * (progress * (progress * 6 - 15) + 10);

        const currentPos = startY + diff * ease;
        window.scrollTo({ left: 0, top: currentPos, behavior: 'instant' });

        if (progress < 1) {
            activeScrollAnim = requestAnimationFrame(step);
        } else {
            activeScrollAnim = null;
            if (onComplete) onComplete();
        }
    }
    activeScrollAnim = requestAnimationFrame(step);
}

window.isUserExpanded = true;
let isScrolledPast = false;
let autoCollapsedOnScroll = false;

function applyCapsuleState(expanded) {
    const capsule = document.getElementById('controlCapsule');
    if (!capsule) return;
    window.isUserExpanded = expanded;
    const bodyCard = document.getElementById('capsuleBodyCard');
    
    if (expanded) {
        capsule.classList.remove('is-collapsed');
        capsule.classList.add('is-expanded');
        if (bodyCard) {
            capsule.style.height = bodyCard.scrollHeight + 'px';
        }
    } else {
        updateCollapsedSummary();
        capsule.classList.remove('is-expanded');
        capsule.classList.add('is-collapsed');
        const isMob = window.innerWidth <= 768;
        capsule.style.height = isMob ? '44px' : '48px';
    }
}

function updateCapsuleScroll(y) {
    const capsule = document.getElementById('controlCapsule');
    if (!capsule) return;
    
    const collapseThreshold = 120;
    const expandThreshold = 15;
    const past = y > collapseThreshold;
    
    if (past !== isScrolledPast) {
        isScrolledPast = past;
        capsule.classList.toggle('is-floating', isScrolledPast);
    }
    
    // 1. Smoothly collapse into floating pill on scroll down past controls
    if (y > collapseThreshold && window.isUserExpanded && !autoCollapsedOnScroll) {
        autoCollapsedOnScroll = true;
        applyCapsuleState(false);
    }
    
    // 2. Smoothly expand back to full controls when reaching the very top
    if (y <= expandThreshold && !window.isUserExpanded && autoCollapsedOnScroll) {
        autoCollapsedOnScroll = false;
        applyCapsuleState(true);
    }
}

function updateCollapsedSummary() {
    const country = document.getElementById('country')?.value || 'United States';
    const mode = document.getElementById('shippingMode')?.value || 'Standard Class';
    const sales = document.getElementById('sales')?.value || '150';
    const days = document.getElementById('daysScheduled')?.value || '3';
    const qty = document.getElementById('quantity')?.value || '1';
    const penalty = document.getElementById('penaltyRate')?.value || '25';
    
    if (document.getElementById('pillScenario')) {
        document.getElementById('pillScenario').textContent = `${country} · ${mode}`;
    }
    if (document.getElementById('pillSales')) {
        document.getElementById('pillSales').textContent = `$${parseFloat(sales).toFixed(2)}`;
    }
    if (document.getElementById('pillDays')) {
        document.getElementById('pillDays').textContent = `${days}d SLA`;
    }
    if (document.getElementById('pillQty')) {
        document.getElementById('pillQty').textContent = `${qty} Unit${parseInt(qty) > 1 ? 's' : ''}`;
    }
    if (document.getElementById('pillPenalty')) {
        document.getElementById('pillPenalty').textContent = `${penalty}% Penalty`;
    }
}

function setupCollapsibleCapsule() {
    const capsule = document.getElementById('controlCapsule');
    const collapseBtn = document.getElementById('capsuleCollapseBtn');
    const editBtn = document.getElementById('pillEditBtn');

    capsule?.addEventListener('click', (e) => {
        if (capsule.classList.contains('is-collapsed')) {
            applyCapsuleState(true);
        }
    });

    editBtn?.addEventListener('click', (e) => {
        e.stopPropagation();
        applyCapsuleState(true);
    });

    collapseBtn?.addEventListener('click', (e) => {
        e.stopPropagation();
        applyCapsuleState(false);
    });
    
    document.addEventListener('click', (e) => {
        if (window.isUserExpanded && capsule && capsule.classList.contains('is-floating') && !capsule.contains(e.target)) {
            applyCapsuleState(false);
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && capsule?.classList.contains('is-expanded')) {
            applyCapsuleState(false);
        }
    });

    const inputs = ['country', 'shippingMode', 'sales', 'daysScheduled', 'quantity', 'penaltyRate'];
    inputs.forEach(id => {
        document.getElementById(id)?.addEventListener('change', updateCollapsedSummary);
        document.getElementById(id)?.addEventListener('input', updateCollapsedSummary);
    });

    const bodyCard = document.getElementById('capsuleBodyCard');
    if (bodyCard && typeof ResizeObserver !== 'undefined') {
        const ro = new ResizeObserver(() => {
            if (window.isUserExpanded && capsule && capsule.classList.contains('is-expanded')) {
                capsule.style.height = bodyCard.scrollHeight + 'px';
            }
        });
        ro.observe(bodyCard);
    }

    setTimeout(() => {
        updateCollapsedSummary();
        applyCapsuleState(window.scrollY <= 15);
    }, 120);
}

function toggleAccordion(id) {
    const el = document.getElementById(id);
    if (el) {
        el.classList.toggle('open');
        const bodyCard = document.getElementById('capsuleBodyCard');
        const capsule = document.getElementById('controlCapsule');
        if (window.isUserExpanded && capsule && bodyCard) {
            requestAnimationFrame(() => {
                capsule.style.height = bodyCard.scrollHeight + 'px';
            });
        }
    }
}

async function runPrediction(autoCollapse = true) {
    const btn = document.getElementById('predictBtn');
    if (!btn) return;
    btn.disabled = true;
    btn.innerHTML = '<span>Analyzing...</span>';
    
    const payload = {
        country: document.getElementById('country').value,
        shipping_mode: document.getElementById('shippingMode').value,
        days_scheduled: parseInt(document.getElementById('daysScheduled').value),
        quantity: parseInt(document.getElementById('quantity').value),
        sales: parseFloat(document.getElementById('sales').value),
        profit: parseFloat(document.getElementById('profit').value),
        penalty_rate: parseFloat(document.getElementById('penaltyRate').value),
        intervention_cost: parseFloat(document.getElementById('interventionCost').value),
        segment: document.getElementById('segment').value,
        payment: document.getElementById('payment').value,
        category: document.getElementById('category').value,
        day: document.getElementById('dayOfWeek').value,
        theme: currentTheme
    };
    
    try {
        const res = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        
        if (data.error) {
            document.getElementById('verdictContainer').innerHTML = 
                `<div class="glass-card" style="color:var(--red);padding:1.5rem;">${data.error}</div>`;
            return;
        }
        
        renderVerdict(data);
        renderFinancials(data.financials);
        renderChart('timelineChart', data.timeline_chart);
        renderChart('shapChart', data.shap_chart);

        // Auto-collapse parameters to sticky summary pill and gracefully glide to results
        if (autoCollapse) {
            applyCapsuleState(false);
            setTimeout(() => {
                const verdictEl = document.getElementById('verdictContainer');
                if (verdictEl) {
                    const top = verdictEl.getBoundingClientRect().top + window.scrollY - 130;
                    gracefulScrollTo(Math.max(0, top), 420);
                }
            }, 180);
        }
    } catch (e) {
        console.error('Prediction error:', e);
        document.getElementById('verdictContainer').innerHTML = 
            `<div class="glass-card" style="color:var(--red);padding:1.5rem;">Request failed. Please try again.</div>`;
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<span>Execute Analysis</span><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" style="margin-left: 6px;"><polygon points="5 3 19 12 5 21 5 3"/></svg>';
    }
}

function renderVerdict(data) {
    const isRisk = data.prediction === 1;
    const probPct = Math.round(data.probability * 100);
    const dashOffset = 440 - (440 * data.probability);
    const color = isRisk ? 'var(--red)' : 'var(--green)';
    const bg = isRisk ? 'rgba(220,38,38,0.12)' : 'rgba(22,163,74,0.12)';
    const subtitle = isRisk ? 'Predicted to violate SLA delivery windows' : 'Predicted to meet SLA schedule';
    
    const container = document.getElementById('verdictContainer');
    if (!container) return;

    container.innerHTML = `
        <div class="glass-card verdict-card ${isRisk ? 'high-risk' : 'on-track'}">
            <div class="verdict-ring">
                <svg viewBox="0 0 160 160">
                    <circle cx="80" cy="80" r="70" fill="none" stroke="var(--border2)" stroke-width="12"/>
                    <circle cx="80" cy="80" r="70" fill="none" stroke="${color}" stroke-width="12"
                        stroke-dasharray="440" stroke-dashoffset="${dashOffset}" stroke-linecap="round"
                        style="transition:stroke-dashoffset 1s ease-out;transform:rotate(-90deg);transform-origin:center;"/>
                </svg>
                <div class="verdict-ring-value" style="color:${color};">${probPct}%</div>
            </div>
            <div class="verdict-info">
                <div class="verdict-label" style="color:${color};">${data.verdict}</div>
                <div class="verdict-title">Risk Probability: ${probPct}%</div>
                <div class="verdict-subtitle">${subtitle}</div>
            </div>
        </div>
    `;
}

function renderFinancials(fin) {
    const isInterventionRec = fin.intervention_recommended === 'Yes';
    const epColor = fin.expected_profit < 0 ? 'var(--red)' : 'var(--green)';
    const epiColor = fin.expected_profit_with_intervention < 0 ? 'var(--red)' : 'var(--green)';
    const profitSavings = Math.abs(fin.expected_profit_with_intervention - fin.expected_profit).toFixed(2);
    
    const container = document.getElementById('financialContainer');
    if (!container) return;

    container.innerHTML = `
        <div class="glass-card form-card prescriptive-result-card" style="margin-bottom: 1rem;">
            <div class="card-title" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px;">
                <span>Prescriptive Strategy & Decision</span>
                <span class="prescriptive-badge ${isInterventionRec ? 'badge-intervene' : 'badge-absorb'}">
                    ${isInterventionRec ? '<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="vertical-align:middle;margin-right:4px;"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>INTERVENTION RECOMMENDED' : '<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="vertical-align:middle;margin-right:4px;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>ABSORB OPERATIONAL RISK'}
                </span>
            </div>
            
            <div class="prescriptive-action-box ${isInterventionRec ? 'box-intervene' : 'box-absorb'}">
                <div class="prescriptive-action-header">
                    ${isInterventionRec ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align:middle;margin-right:5px;"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>Action: Expedite Shipping Freight' : '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align:middle;margin-right:5px;"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>Action: Maintain Standard Fulfillment'}
                </div>
                <div class="prescriptive-action-desc">
                    ${isInterventionRec 
                        ? `Expedited freight protects <strong>$${fin.sales.toFixed(2)}</strong> order revenue from a potential <strong>$${fin.penalty_loss.toFixed(2)}</strong> SLA violation penalty, delivering a net profit gain of <strong>+$${profitSavings}</strong> over inaction.` 
                        : `SLA delay liability is lower than the expedited freight cost. Standard shipping yields the highest expected net profit margin of <strong>$${fin.expected_profit.toFixed(2)}</strong>.`
                    }
                </div>
            </div>

            <div class="financial-grid" style="grid-template-columns: repeat(auto-fit, minmax(125px, 1fr)); margin-top: 0.85rem; gap: 0.65rem;">
                <div class="financial-item">
                    <div class="financial-label">Base Order Profit</div>
                    <div class="financial-value" style="color:var(--text); font-size:1.05rem;">$${fin.profit.toFixed(2)}</div>
                </div>
                <div class="financial-item">
                    <div class="financial-label">Penalty Loss Liability</div>
                    <div class="financial-value" style="color:var(--red); font-size:1.05rem;">-$${fin.penalty_loss.toFixed(2)}</div>
                </div>
                <div class="financial-item">
                    <div class="financial-label">Exp. Profit (No Action)</div>
                    <div class="financial-value" style="color:${epColor}; font-size:1.05rem;">$${fin.expected_profit.toFixed(2)}</div>
                </div>
                <div class="financial-item" style="border: 1px solid ${isInterventionRec ? 'rgba(13,148,136,0.45)' : 'var(--border)'}; background: ${isInterventionRec ? 'rgba(13,148,136,0.08)' : 'var(--bg3)'};">
                    <div class="financial-label">Exp. Profit (Expedited)</div>
                    <div class="financial-value" style="color:${epiColor}; font-size:1.05rem;">$${fin.expected_profit_with_intervention.toFixed(2)}</div>
                </div>
            </div>

            <!-- Strategy Formula & Technical Meta -->
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.4rem; margin-top:0.85rem; padding-top:0.65rem; border-top:1px solid var(--border);">
                <span style="font-size:0.7rem; color:var(--text3);">Decision Rule: <code>Expected Profit (No Action) &lt; Expected Profit (Expedited)</code></span>
                <div style="display:flex; gap:0.35rem; flex-wrap:wrap;">
                    <span class="tech-tag">RandomForest v3.0</span>
                    <span class="tech-tag">71.9% AUC</span>
                    <span class="tech-tag">SHAP TreeExplainer</span>
                </div>
            </div>
        </div>
    `;
}

function renderChart(divId, data) {
    if (!data || data.error) {
        const el = document.getElementById(divId);
        if (el) el.innerHTML = `<p style="color:var(--text3);text-align:center;padding:1.5rem;font-size:0.8rem;">${data ? data.error : 'Chart unavailable'}</p>`;
        return;
    }
    
    const el = document.getElementById(divId);
    if (!el || typeof echarts === 'undefined') return;
    
    // Initialize or get ECharts instance
    let chart = echarts.getInstanceByDom(el);
    if (!chart) chart = echarts.init(el);
    
    const isDark = currentTheme === 'dark';
    const textColor = isDark ? '#cbd5e1' : '#475569';
    const titleColor = isDark ? '#f8fafc' : '#0f172a';
    const splitLineColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(15,23,42,0.08)';
    const accentColor = isDark ? '#38bdf8' : '#0d9488';
    const redColor = isDark ? '#f87171' : '#dc2626';
    const greenColor = isDark ? '#34d399' : '#16a34a';

    let option = {};
    
    if (divId === 'importanceChart') {
        option = {
            tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
            grid: { left: 4, right: 35, bottom: 6, top: 8, containLabel: true },
            xAxis: { type: 'value', show: false, splitLine: { show: false } },
            yAxis: { type: 'category', data: data.labels, axisLine: { lineStyle: { color: splitLineColor } }, axisLabel: { color: textColor, fontSize: 10 } },
            series: [
                {
                    name: 'Importance',
                    type: 'bar',
                    data: data.values.map((v, i) => ({
                        value: v,
                        itemStyle: { color: i > data.values.length - 4 ? accentColor : '#94A3B8' }
                    })),
                    barWidth: '60%',
                    label: { show: true, position: 'right', color: textColor, fontSize: 10, formatter: (p) => data.pct[p.dataIndex].toFixed(1) + '%' }
                }
            ]
        };
    } else if (divId === 'timelineChart') {
        const mx = Math.max(data.sched, data.proj) + 2;
        const color = data.pred === 1 ? redColor : greenColor;
        option = {
            tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
            grid: { left: 4, right: 45, bottom: 8, top: 8, containLabel: true },
            xAxis: { type: 'value', max: mx, splitLine: { show: true, lineStyle: { color: splitLineColor } }, axisLabel: { color: textColor, fontSize: 10 } },
            yAxis: { type: 'category', data: ['Projected', 'Scheduled SLA'], axisLine: { show: false }, axisLabel: { color: textColor, fontWeight: 'bold', fontSize: 11 } },
            series: [
                {
                    name: 'Days',
                    type: 'bar',
                    data: [
                        { value: data.proj, itemStyle: { color: color } },
                        { value: data.sched, itemStyle: { color: '#94a3b8' } }
                    ],
                    barWidth: '42%',
                    label: { show: true, position: 'right', color: textColor, fontSize: 11, fontWeight: '600', formatter: '{c} Days' }
                }
            ]
        };
    } else if (divId === 'shapChart') {
        const labels = data.labels || [];
        const values = data.values || [];
        
        // Build individual vertical bar objects with bidirectional coloring
        const barData = values.map((val, idx) => {
            const isPos = val >= 0;
            return {
                value: val,
                name: labels[idx] || `Factor ${idx + 1}`,
                itemStyle: {
                    color: isPos 
                        ? (isDark ? '#f87171' : '#dc2626')
                        : (isDark ? '#34d399' : '#16a34a'),
                    borderRadius: isPos ? [4, 4, 0, 0] : [0, 0, 4, 4]
                }
            };
        });

        option = {
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'shadow' },
                formatter: function (params) {
                    const item = params[0];
                    if (!item) return '';
                    const val = item.value;
                    const isPos = val >= 0;
                    const dot = isPos 
                        ? `<span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:${redColor};margin-right:5px;vertical-align:middle;"></span>` 
                        : `<span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:${greenColor};margin-right:5px;vertical-align:middle;"></span>`;
                    const effect = isPos ? 'Increases Delay Risk' : 'Reduces Delay Risk';
                    const sign = val > 0 ? '+' : '';
                    return `
                        <div style="font-weight:700;font-size:12px;margin-bottom:3px;color:${titleColor};">${item.name}</div>
                        <div style="font-size:11px;color:${isPos ? redColor : greenColor};">
                            ${dot}${effect}: <b>${sign}${val.toFixed(3)}</b>
                        </div>
                    `;
                }
            },
            grid: { left: 6, right: 6, bottom: 26, top: 22, containLabel: true },
            xAxis: {
                type: 'category',
                data: labels,
                axisTick: { show: false },
                axisLine: { 
                    lineStyle: { color: splitLineColor } 
                },
                axisLabel: {
                    color: textColor,
                    fontSize: 10,
                    interval: 0,
                    formatter: function(val) {
                        if (val.length > 12) {
                            const words = val.split(' ');
                            if (words.length > 1) {
                                const mid = Math.ceil(words.length / 2);
                                return words.slice(0, mid).join(' ') + '\n' + words.slice(mid).join(' ');
                            }
                            return val.slice(0, 10) + '..';
                        }
                        return val;
                    }
                }
            },
            yAxis: {
                type: 'value',
                splitLine: { show: true, lineStyle: { color: splitLineColor } },
                axisLine: { 
                    show: true,
                    lineStyle: { color: isDark ? 'rgba(255,255,255,0.15)' : 'rgba(15,23,42,0.15)' } 
                },
                axisLabel: { 
                    color: textColor, 
                    fontSize: 9,
                    formatter: function(v) {
                        return (v > 0 ? '+' : '') + v.toFixed(2);
                    }
                }
            },
            series: [
                {
                    name: 'SHAP Impact',
                    type: 'bar',
                    barWidth: '40%',
                    data: barData,
                    label: {
                        show: true,
                        position: 'top',
                        color: textColor,
                        fontSize: 10,
                        fontWeight: '600',
                        formatter: function(p) {
                            const v = p.value;
                            return (v > 0 ? '+' : '') + v.toFixed(2);
                        }
                    }
                }
            ]
        };
    } else if (divId === 'batchMapChart') {
        option = {
            tooltip: { trigger: 'item', formatter: '{b}<br/>Delay Rate: {c}%' },
            visualMap: { min: 0, max: 100, text: ['High', 'Low'], inRange: { color: ['#fee2e2', '#b91c1c'] }, textStyle: { color: textColor, fontSize: 10 } },
            series: [
                {
                    name: 'Delay Rate',
                    type: 'map',
                    map: 'world',
                    roam: true,
                    label: { show: false },
                    itemStyle: { areaColor: isDark ? '#1e293b' : '#f1f5f9', borderColor: splitLineColor },
                    emphasis: { itemStyle: { areaColor: accentColor } },
                    data: data
                }
            ]
        };
    } else if (divId === 'batchRoiChart') {
        option = {
            tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
            grid: { left: 4, right: 40, bottom: 6, top: 8, containLabel: true },
            xAxis: { type: 'value', splitLine: { show: false }, axisLabel: { color: textColor, fontSize: 10 } },
            yAxis: { type: 'category', data: data.map(d => d.category), axisLine: { lineStyle: { color: splitLineColor } }, axisLabel: { color: textColor, fontSize: 10 } },
            series: [
                {
                    name: 'Savings ($)',
                    type: 'bar',
                    data: data.map(d => ({ value: d.savings, itemStyle: { color: greenColor } })),
                    barWidth: '60%',
                    label: { show: true, position: 'right', color: textColor, fontSize: 10, formatter: (p) => '$' + p.value.toFixed(0) }
                }
            ]
        };
    }
    
    chart.setOption(option, true);
    
    // Auto-ResizeObserver for seamless adaptation to any screen size, orientation & container change
    if (!el._resizeObserver && typeof ResizeObserver !== 'undefined') {
        el._resizeObserver = new ResizeObserver(() => {
            chart.resize();
        });
        el._resizeObserver.observe(el);
    }
}

async function loadImportanceChart() {
    try {
        const res = await fetch(`/api/charts/importance?theme=${currentTheme}`);
        const data = await res.json();
        renderChart('importanceChart', data.chart);
    } catch (e) {
        console.error('Importance chart error:', e);
    }
}

async function runBatch() {
    const btn = document.getElementById('batchBtn');
    const fileInput = document.getElementById('fileInput');
    
    if (!btn || !fileInput) return;

    if (!fileInput.files.length) {
        document.getElementById('batchMessage').innerHTML = 
            '<div class="glass-card" style="color:var(--red);padding:1rem;">Please upload a file first.</div>';
        return;
    }
    
    btn.disabled = true;
    btn.textContent = 'Processing...';
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('penalty_rate', document.getElementById('bulkPenaltyRate').value);
    formData.append('intervention_cost', document.getElementById('bulkInterventionCost').value);
    formData.append('theme', currentTheme);
    
    try {
        const res = await fetch('/api/batch', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        
        if (!data.success) {
            document.getElementById('batchMessage').innerHTML = 
                `<div class="glass-card" style="color:var(--red);padding:1rem;">${data.message}</div>`;
            return;
        }
        
        // Show success message
        document.getElementById('batchMessage').innerHTML = 
            `<div class="glass-card" style="color:var(--green);padding:0.8rem;font-weight:600;font-size:0.85rem;">\u2705 ${data.message}</div>`;
        
        // Render KPIs
        renderBatchKpis(data.kpis);
        
        // Render results table
        renderBatchTable(data.results);
        
        // Show download button
        if (data.download_filename) {
            const dlContainer = document.getElementById('batchDownloadContainer');
            if (dlContainer) {
                dlContainer.style.display = 'block';
                const dlBtn = document.getElementById('batchDownloadBtn');
                if (dlBtn) dlBtn.href = `/api/batch/download/${data.download_filename}`;
            }
        }
        
        // Render charts
        const chartsRow = document.getElementById('batchChartsRow');
        if (chartsRow) chartsRow.style.display = 'grid';
        renderChart('batchMapChart', data.map_chart);
        renderChart('batchRoiChart', data.roi_chart);
        
    } catch (e) {
        console.error('Batch error:', e);
        document.getElementById('batchMessage').innerHTML = 
            '<div class="glass-card" style="color:var(--red);padding:1rem;">Batch processing failed. Please try again.</div>';
    } finally {
        btn.disabled = false;
        btn.textContent = 'Execute Batch Analysis';
    }
}

function renderBatchKpis(kpis) {
    if (!kpis) return;
    const formatCurrency = (v) => {
        if (Math.abs(v) >= 1000) return `$${(v/1000).toFixed(1)}K`;
        return `$${v.toFixed(0)}`;
    };
    
    const container = document.getElementById('batchKpiContainer');
    if (!container) return;

    container.innerHTML = `
        <div class="kpi-grid" style="margin-top:1rem;">
            <div class="glass-card kpi-card">
                <div class="kpi-label">Total Volume</div>
                <div class="kpi-value">${kpis.total_orders}</div>
                <div class="kpi-sub">Orders Processed</div>
            </div>
            <div class="glass-card kpi-card">
                <div class="kpi-label">Total Revenue</div>
                <div class="kpi-value">${formatCurrency(kpis.total_revenue)}</div>
                <div class="kpi-sub">Batch Value</div>
            </div>
            <div class="glass-card kpi-card">
                <div class="kpi-label">High Risk Orders</div>
                <div class="kpi-value" style="color:var(--red);">${kpis.high_risk_orders}</div>
                <div class="kpi-sub">${kpis.delay_rate.toFixed(1)}% of Batch</div>
            </div>
            <div class="glass-card kpi-card">
                <div class="kpi-label">Value at Risk</div>
                <div class="kpi-value" style="color:var(--red);">${formatCurrency(kpis.value_at_risk)}</div>
                <div class="kpi-sub">Potential Penalties</div>
            </div>
            <div class="glass-card kpi-card" style="border-color:var(--green);">
                <div class="kpi-label" style="color:var(--green);">ROI / Savings</div>
                <div class="kpi-value" style="color:var(--green);">${formatCurrency(kpis.roi_savings)}</div>
                <div class="kpi-sub">Net Mitigation Return</div>
            </div>
        </div>
    `;
}

function renderBatchTable(results) {
    if (!results || !results.length) return;
    
    const container = document.getElementById('batchTableContainer');
    if (container) container.style.display = 'block';
    
    const table = document.getElementById('batchResultsTable');
    if (!table) return;

    // Get column headers from first result
    const cols = Object.keys(results[0]);
    
    // Limit to key output columns for display
    const displayCols = cols.slice(0, 10); // Show first 10 columns
    
    let html = '<thead><tr>';
    displayCols.forEach(col => {
        html += `<th>${col}</th>`;
    });
    html += '</tr></thead><tbody>';
    
    results.forEach(row => {
        html += '<tr>';
        displayCols.forEach(col => {
            let val = row[col];
            let cellClass = '';
            
            if (col === 'Late Delivery Flag') {
                if (String(val).includes('Risk')) {
                    cellClass = 'badge-risk';
                } else {
                    cellClass = 'badge-safe';
                }
                val = `<span class="${cellClass}">${val}</span>`;
            } else if (typeof val === 'number') {
                val = val.toFixed(2);
            }
            
            html += `<td>${val !== null && val !== undefined ? val : ''}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody>';
    
    table.innerHTML = html;
}


// Add scroll listener for dynamic top nav capsule glassmorphism and adaptive control capsule
window.addEventListener('scroll', () => {
    const y = window.scrollY;
    const nav = document.getElementById('topNav');
    if (y > 20) {
        if (nav) nav.classList.add('scrolled');
        document.body.classList.add('nav-scrolled');
    } else {
        if (nav) nav.classList.remove('scrolled');
        document.body.classList.remove('nav-scrolled');
    }
    updateCapsuleScroll(y);
}, { passive: true });

// Prevent Render from sleeping when user has tab open
setInterval(() => {
    fetch('/api/config').catch(() => {});
    console.log('Frontend heartbeat ping sent');
}, 600000); // 10 minutes
