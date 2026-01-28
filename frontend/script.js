// ============== Configuration ==============
const API_URL = 'http://localhost:8000';

// ============== DOM Elements ==============
const form = document.getElementById('generateForm');
const submitBtn = document.getElementById('submitBtn');
const btnText = submitBtn.querySelector('.btn-text');
const btnLoading = submitBtn.querySelector('.btn-loading');

const pipelineSection = document.getElementById('pipelineSection');
const resultsSection = document.getElementById('resultsSection');

// Pipeline steps
const step1 = document.getElementById('step1');
const step2 = document.getElementById('step2');
const step3 = document.getElementById('step3');
const refineArrow = document.getElementById('refineArrow');

// Result cards
const initialCard = document.getElementById('initialCard');
const reviewCard = document.getElementById('reviewCard');
const refinedCard = document.getElementById('refinedCard');
const refinedReviewCard = document.getElementById('refinedReviewCard');
const finalCard = document.getElementById('finalCard');

// ============== Form Submission ==============
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const grade = parseInt(document.getElementById('grade').value);
    const topic = document.getElementById('topic').value.trim();
    
    if (!grade || !topic) {
        alert('Please fill in all fields');
        return;
    }
    
    await runPipeline(grade, topic);
});

// ============== Main Pipeline Function ==============
async function runPipeline(grade, topic) {
    // Reset UI
    resetUI();
    
    // Show loading state
    setLoading(true);
    pipelineSection.style.display = 'block';
    
    // Animate step 1 (Generator)
    updateStep(step1, 'active', 'Running...');
    
    try {
        // Call API
        const response = await fetch(`${API_URL}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ grade, topic })
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update pipeline visualization
        updateStep(step1, 'complete', 'Done ✓');
        updateStep(step2, 'complete', data.initial_review.status === 'pass' ? 'Passed ✓' : 'Failed ✗');
        
        if (data.was_refined) {
            step3.style.display = 'block';
            refineArrow.style.display = 'block';
            updateStep(step3, 'complete', 'Done ✓');
        }
        
        // Show results
        displayResults(data);
        
    } catch (error) {
        console.error('Pipeline error:', error);
        updateStep(step1, 'failed', 'Error');
        alert(`Error: ${error.message}`);
    } finally {
        setLoading(false);
    }
}

// ============== Display Functions ==============
function displayResults(data) {
    resultsSection.style.display = 'flex';
    
    // Initial content
    displayContent('initial', data.initial_output);
    
    // Initial review
    displayReview('review', data.initial_review);
    
    // Refined content (if applicable)
    if (data.was_refined && data.refined_output) {
        refinedCard.style.display = 'block';
        displayContent('refined', data.refined_output);
        
        if (data.refined_review) {
            refinedReviewCard.style.display = 'block';
            displayReview('refinedReview', data.refined_review);
        }
    }
    
    // Final result
    displayFinalResult(data);
}

function displayContent(prefix, content) {
    // Explanation
    document.getElementById(`${prefix}Explanation`).textContent = content.explanation;
    
    // MCQs
    const mcqsContainer = document.getElementById(`${prefix}Mcqs`);
    mcqsContainer.innerHTML = content.mcqs.map((mcq, index) => `
        <div class="mcq-item">
            <div class="mcq-question">Q${index + 1}: ${mcq.question}</div>
            <div class="mcq-options">
                ${mcq.options.map(opt => `
                    <div class="mcq-option ${opt.startsWith(mcq.answer) ? 'correct' : ''}">
                        ${opt}
                    </div>
                `).join('')}
            </div>
            <div class="mcq-answer">✓ Correct Answer: ${mcq.answer}</div>
        </div>
    `).join('');
}

function displayReview(prefix, review) {
    // Status
    const statusEl = document.getElementById(`${prefix}Status`);
    statusEl.className = `review-status ${review.status}`;
    statusEl.innerHTML = review.status === 'pass' 
        ? '✅ PASSED' 
        : '❌ FAILED - Needs Refinement';
    
    // Scores
    const scoresEl = document.getElementById(`${prefix}Scores`);
    if (review.scores) {
        scoresEl.innerHTML = Object.entries(review.scores).map(([key, value]) => `
            <div class="score-item">
                <div class="score-label">${formatLabel(key)}</div>
                <div class="score-value ${getScoreClass(value)}">${value}/10</div>
            </div>
        `).join('');
    }
    
    // Feedback
    const feedbackEl = document.getElementById(`${prefix}Feedback`);
    if (review.feedback && review.feedback.length > 0) {
        feedbackEl.innerHTML = `
            <h4>Feedback</h4>
            ${review.feedback.map(fb => `
                <div class="feedback-item">
                    <span>💡</span>
                    <span>${fb}</span>
                </div>
            `).join('')}
        `;
    } else {
        feedbackEl.innerHTML = '<p style="color: var(--success);">No issues found! ✓</p>';
    }
}

function displayFinalResult(data) {
    const finalStatus = document.getElementById('finalStatus');
    finalStatus.className = `final-status ${data.final_status}`;
    finalStatus.textContent = data.final_status.toUpperCase();
    
    const finalSummary = document.getElementById('finalSummary');
    if (data.was_refined) {
        finalSummary.innerHTML = `
            <p>The content required <strong>one refinement pass</strong> to meet quality standards.</p>
            <p>Final status: <strong>${data.final_status.toUpperCase()}</strong></p>
        `;
    } else {
        finalSummary.innerHTML = `
            <p>The content <strong>passed on the first attempt</strong>! No refinement was needed.</p>
            <p>Final status: <strong>${data.final_status.toUpperCase()}</strong></p>
        `;
    }
}

// ============== Helper Functions ==============
function setLoading(loading) {
    submitBtn.disabled = loading;
    btnText.style.display = loading ? 'none' : 'inline';
    btnLoading.style.display = loading ? 'inline' : 'none';
}

function resetUI() {
    // Reset pipeline steps
    [step1, step2, step3].forEach(step => {
        step.className = 'pipeline-step';
        step.querySelector('.step-status').textContent = 'Pending';
    });
    step3.style.display = 'none';
    refineArrow.style.display = 'none';
    
    // Hide results
    resultsSection.style.display = 'none';
    refinedCard.style.display = 'none';
    refinedReviewCard.style.display = 'none';
}

function updateStep(stepEl, status, text) {
    stepEl.className = `pipeline-step ${status}`;
    stepEl.querySelector('.step-status').textContent = text;
}

function formatLabel(key) {
    return key.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
}

function getScoreClass(score) {
    if (score >= 8) return 'high';
    if (score >= 6) return 'medium';
    return 'low';
}