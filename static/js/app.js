// Object Detection Web App JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const fileInput = document.getElementById('file-input');
    const selectButton = document.getElementById('select-button');
    const uploadArea = document.getElementById('upload-area');
    const previewContainer = document.getElementById('preview-container');
    const previewImage = document.getElementById('preview-image');
    const loading = document.getElementById('loading');
    const resultsContainer = document.getElementById('results-container');
    const detectionSummary = document.getElementById('detection-summary');
    const jsonOutput = document.getElementById('json-output');
    const recipeContent = document.getElementById('recipe-content');
    const generateRecipeCheck = document.getElementById('generate-recipe-check');
    const recipeType = document.getElementById('recipe-type');
    
    // Recipe generation steps elements
    const step1 = document.getElementById('step1');
    const step2 = document.getElementById('step2');
    const step3 = document.getElementById('step3');
    
    // Initialize AOS animations
    AOS.init({
        duration: 800,
        easing: 'ease',
        once: false,
        mirror: false
    });
    
    // Colors for bounding boxes (COCO classes)
    const colors = [
        '#FF3838', '#FF9D97', '#FF701F', '#FFB21D', '#CFD231', 
        '#48F90A', '#92CC17', '#3DDB86', '#1A9334', '#00D4BB',
        '#2C99A8', '#00C2FF', '#344593', '#6473FF', '#0018EC', 
        '#8438FF', '#520085', '#CB38FF', '#FF95C8', '#FF37C7'
    ];
    
    // Setup click to select
    if (selectButton) {
        selectButton.addEventListener('click', function() {
            fileInput.click();
        });
    }
    
    // Setup drag and drop
    if (uploadArea) {
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.style.backgroundColor = '#e9ecef';
        });
        
        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadArea.style.backgroundColor = '#f0f0f0';
        });
        
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.style.backgroundColor = '#f0f0f0';
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                handleFile(e.dataTransfer.files[0]);
            }
        });
    }
    
    // Handle file selection
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (fileInput.files.length) {
                handleFile(fileInput.files[0]);
            }
        });
    }
    
    // Smooth scroll for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                window.scrollTo({
                    top: target.offsetTop - 70,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Handle recipe generation animation steps
    function startRecipeGenerationAnimation() {
        if (!step1 || !step2 || !step3) return;
        
        // Reset all steps
        step1.classList.remove('step-active');
        step2.classList.remove('step-active');
        step3.classList.remove('step-active');
        
        // Activate first step immediately
        setTimeout(() => {
            step1.classList.add('step-active');
        }, 500);
        
        // Activate second step after delay
        setTimeout(() => {
            step2.classList.add('step-active');
        }, 3000);
        
        // Activate third step after longer delay
        setTimeout(() => {
            step3.classList.add('step-active');
        }, 5500);
    }
    
    // Handle file upload and processing
    function handleFile(file) {
        // First, show the preview
        const imageUrl = URL.createObjectURL(file);
        previewImage.src = imageUrl;
        previewContainer.style.display = 'block';
        
        // Add fade-in animation to preview container
        previewContainer.classList.add('fade-in');
        
        // Clear previous bounding boxes
        const existingBoxes = previewContainer.querySelectorAll('.bounding-box, .detection-label');
        existingBoxes.forEach(box => box.remove());
        
        // Show loading indicator
        loading.style.display = 'block';
        
        // Start recipe generation animation if recipe is requested
        if (generateRecipeCheck && generateRecipeCheck.checked) {
            startRecipeGenerationAnimation();
        }
        
        // Scroll to loading indicator
        setTimeout(() => {
            loading.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 300);
        
        // Prepare form data for upload
        const formData = new FormData();
        formData.append('file', file);
        
        // Add recipe generation parameters if available
        if (generateRecipeCheck && recipeType) {
            formData.append('generate_recipe', generateRecipeCheck.checked);
            formData.append('recipe_type', recipeType.value);
        }
        
        // Send file to server for detection
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loading.style.display = 'none';
            resultsContainer.style.display = 'block';
            
            // Add fade-in animation to results container
            resultsContainer.classList.add('fade-in');
            
            // Scroll to results
            setTimeout(() => {
                resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 300);
            
            if (data.status === 'success') {
                // Show JSON data
                jsonOutput.textContent = JSON.stringify(data.detections, null, 2);
                
                // Create summary
                let summaryHTML = '';
                if (data.count > 0) {
                    summaryHTML = `<div class="alert alert-success mb-4">
                        <h5>Found ${data.count} object(s) in the image!</h5>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Object</th>
                                    <th>Confidence</th>
                                    <th>Coordinates [x1, y1, x2, y2]</th>
                                </tr>
                            </thead>
                            <tbody>`;
                    
                    data.detections.forEach((detection, index) => {
                        // Get bounding box coordinates
                        const bbox = detection.box || detection.bbox;
                        
                        summaryHTML += `<tr>
                            <td>${index + 1}</td>
                            <td>${detection.label}</td>
                            <td>${(detection.score * 100).toFixed(2)}%</td>
                            <td>[${bbox.map(coord => Math.round(coord)).join(', ')}]</td>
                        </tr>`;
                    });
                    
                    summaryHTML += `</tbody></table></div>`;
                } else {
                    summaryHTML = `<div class="alert alert-warning">
                        <h5>No objects detected in this image.</h5>
                    </div>`;
                }
                
                detectionSummary.innerHTML = summaryHTML;
                
                // Handle recipe data if available
                if (recipeContent && data.recipe) {
                    displayRecipe(data.recipe);
                    
                    // Auto-switch to recipe tab if we have recipe data
                    if (data.recipe.success && data.recipe.recipe) {
                        const recipeTab = document.getElementById('recipe-tab');
                        if (recipeTab) {
                            setTimeout(() => {
                                recipeTab.click();
                                
                                // Add animation class to recipe content
                                if (recipeContent) {
                                    recipeContent.classList.add('active');
                                }
                                
                                // Refresh AOS animations
                                setTimeout(() => {
                                    AOS.refresh();
                                }, 500);
                            }, 500);
                        }
                    }
                }
                
                // Wait for image to load to draw bounding boxes
                previewImage.onload = function() {
                    drawBoundingBoxes(data.detections, previewImage);
                };
                
                // If image is already loaded
                if (previewImage.complete) {
                    drawBoundingBoxes(data.detections, previewImage);
                }
            } else {
                // Show error
                detectionSummary.innerHTML = `<div class="alert alert-danger">
                    <h5>Error</h5>
                    <p>${data.message}</p>
                </div>`;
                jsonOutput.textContent = "Error: " + data.message;
            }
        })
        .catch(error => {
            loading.style.display = 'none';
            resultsContainer.style.display = 'block';
            
            // Add fade-in animation
            resultsContainer.classList.add('fade-in');
            
            detectionSummary.innerHTML = `<div class="alert alert-danger">
                <h5>Error</h5>
                <p>Network error: ${error.message}</p>
            </div>`;
            jsonOutput.textContent = "Network error: " + error.message;
            
            // Scroll to results
            setTimeout(() => {
                resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 300);
        });
    }
    
    // Draw bounding boxes on the image
    function drawBoundingBoxes(detections, image) {
        // Get image dimensions as displayed on the page
        const imageWidth = image.width;
        const imageHeight = image.height;
        
        // Get actual image dimensions
        const naturalWidth = image.naturalWidth;
        const naturalHeight = image.naturalHeight;
        
        // Calculate scaling factors
        const scaleX = imageWidth / naturalWidth;
        const scaleY = imageHeight / naturalHeight;
        
        // Clear previous bounding boxes
        const existingBoxes = previewContainer.querySelectorAll('.bounding-box, .detection-label');
        existingBoxes.forEach(box => box.remove());
        
        // Get the image container for positioning
        const imageContainer = previewImage.parentElement;
        
        // Calculate offset for absolute positioning
        const rect = image.getBoundingClientRect();
        const containerRect = imageContainer.getBoundingClientRect();
        const offsetX = rect.left - containerRect.left;
        const offsetY = rect.top - containerRect.top;
        
        // Loop through detections and draw bounding boxes
        detections.forEach((detection, index) => {
            // Get bounding box coordinates (handle different formats)
            const bbox = detection.box || detection.bbox || [0, 0, 0, 0];
            
            // Create the bounding box element
            const box = document.createElement('div');
            box.className = 'bounding-box';
            
            // Position and size the box
            const x = bbox[0] * scaleX + offsetX;
            const y = bbox[1] * scaleY + offsetY;
            const width = (bbox[2] - bbox[0]) * scaleX;
            const height = (bbox[3] - bbox[1]) * scaleY;
            
            box.style.left = `${x}px`;
            box.style.top = `${y}px`;
            box.style.width = `${width}px`;
            box.style.height = `${height}px`;
            
            // Set color based on detection index
            const colorIndex = index % colors.length;
            box.style.borderColor = colors[colorIndex];
            
            // Create label
            const label = document.createElement('div');
            label.className = 'detection-label';
            label.style.backgroundColor = colors[colorIndex];
            label.textContent = `${detection.label} (${(detection.score * 100).toFixed(1)}%)`;
            
            // Position label
            label.style.left = `${x}px`;
            label.style.top = `${y - 25}px`;
            
            // Add to DOM
            imageContainer.appendChild(box);
            imageContainer.appendChild(label);
            
            // Add animation
            setTimeout(() => {
                box.style.transition = 'all 0.3s ease';
                label.style.transition = 'all 0.3s ease';
            }, 50);
        });
    }
    
    // Display recipe data in a nice format
    function displayRecipe(recipeData) {
        if (!recipeContent) return;
        
        if (recipeData.success && recipeData.recipe) {
            const recipe = recipeData.recipe;
            
            let html = `<div class="recipe-card" data-aos="fade-up">
                <div class="recipe-header">
                    <h2 class="recipe-title">${recipe.title || 'Recipe'}</h2>
                    <p class="lead">Based on detected ingredients: ${recipeData.detected_items?.join(', ') || 'None'}</p>
                </div>
                
                <div class="row">
                    <div class="col-md-5" data-aos="fade-right" data-aos-delay="200">
                        <h4>Ingredients</h4>
                        <ul class="ingredient-list">`;
            
            // Add ingredients
            if (recipe.ingredients && recipe.ingredients.length > 0) {
                recipe.ingredients.forEach((ingredient, index) => {
                    html += `<li data-aos="fade-up" data-aos-delay="${200 + (index * 50)}">${ingredient}</li>`;
                });
            } else {
                html += `<li>No ingredients specified</li>`;
            }
            
            html += `</ul>
                    </div>
                    
                    <div class="col-md-7" data-aos="fade-left" data-aos-delay="200">
                        <h4>Instructions</h4>
                        <ol class="instruction-list">`;
            
            // Add instructions
            if (recipe.instructions && recipe.instructions.length > 0) {
                recipe.instructions.forEach((step, index) => {
                    html += `<li data-aos="fade-up" data-aos-delay="${200 + (index * 100)}">${step}</li>`;
                });
            } else {
                html += `<li>No instructions specified</li>`;
            }
            
            html += `</ol>
                    </div>
                </div>`;
            
            // Add serving suggestions if available
            if (recipe.serving_suggestions) {
                html += `<div class="serving-section mt-4" data-aos="fade-up" data-aos-delay="400">
                    <h4>Serving Suggestions</h4>
                    <p>${recipe.serving_suggestions}</p>
                </div>`;
            }
            
            // Add nutritional notes if available
            if (recipe.nutritional_notes) {
                html += `<div class="nutrition-section mt-3" data-aos="fade-up" data-aos-delay="500">
                    <h4>Nutritional Notes</h4>
                    <p>${recipe.nutritional_notes}</p>
                </div>`;
            }
            
            // Add note if this is a fallback recipe
            if (recipeData.note) {
                html += `<div class="alert alert-info mt-3" data-aos="fade-up" data-aos-delay="600">
                    <p><strong>Note:</strong> ${recipeData.note}</p>
                </div>`;
            }
            
            // Add team credits
            html += `<div class="mt-5 pt-2 border-top" data-aos="fade-up" data-aos-delay="700">
                <p class="text-center text-muted mb-0">Recipe generated by the Culinary Vision Team: Atul Kumar, Neha Nayak, Chaitanya, Alex, Mohak, Abhinav</p>
            </div>`;
            
            html += `</div>`;
            
            recipeContent.innerHTML = html;
            
            // Initialize AOS for newly added elements
            setTimeout(() => {
                AOS.refresh();
            }, 100);
        } else if (recipeData.message) {
            // Show message if provided
            recipeContent.innerHTML = `<div class="alert alert-info">
                <h5>No Recipe Generated</h5>
                <p>${recipeData.message}</p>
            </div>`;
        } else if (recipeData.error) {
            // Show error
            recipeContent.innerHTML = `<div class="alert alert-danger">
                <h5>Error</h5>
                <p>${recipeData.error}</p>
            </div>`;
        } else {
            // Generic message
            recipeContent.innerHTML = `<div class="alert alert-warning">
                <h5>No Recipe Available</h5>
                <p>Could not generate a recipe from the detected items.</p>
            </div>`;
        }
    }
    
    // Copy JSON data to clipboard
    window.copyJsonToClipboard = function() {
        const jsonText = jsonOutput.textContent;
        navigator.clipboard.writeText(jsonText).then(() => {
            const copyBtn = document.getElementById('copy-btn');
            copyBtn.textContent = 'Copied!';
            copyBtn.classList.add('btn-success');
            copyBtn.classList.remove('btn-light');
            
            setTimeout(() => {
                copyBtn.textContent = 'Copy JSON';
                copyBtn.classList.remove('btn-success');
                copyBtn.classList.add('btn-light');
            }, 2000);
        });
    }
    
    // Tab handling - adding animation
    const tabLinks = document.querySelectorAll('.nav-tabs .nav-link');
    if (tabLinks.length) {
        tabLinks.forEach(tab => {
            tab.addEventListener('click', function() {
                const target = document.querySelector(this.dataset.bsTarget);
                if (target && this.id === 'recipe-tab') {
                    setTimeout(() => {
                        if (recipeContent) {
                            recipeContent.classList.add('active');
                            
                            // Refresh AOS animations when switching to recipe tab
                            setTimeout(() => {
                                AOS.refresh();
                            }, 300);
                        }
                    }, 150);
                }
            });
        });
    }
}); 