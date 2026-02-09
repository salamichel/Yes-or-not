(function() {
    'use strict';

    function initDropzone() {
        // Find the EventMedia inline group
        var inlineGroup = document.querySelector('.inline-group[id*="media"]');
        if (!inlineGroup) return;

        // Create dropzone element
        var dropzone = document.createElement('div');
        dropzone.className = 'event-media-dropzone';
        dropzone.innerHTML =
            '<span class="dropzone-icon">&#128247;</span>' +
            '<p>Glissez-d\u00e9posez vos photos et vid\u00e9os ici</p>' +
            '<p class="dropzone-hint">ou cliquez pour s\u00e9lectionner des fichiers (JPG, PNG, MP4)</p>';

        // Hidden file input
        var fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.multiple = true;
        fileInput.accept = 'image/*,video/mp4,video/webm';
        fileInput.style.display = 'none';
        dropzone.appendChild(fileInput);

        // Preview grid
        var previewGrid = document.createElement('div');
        previewGrid.className = 'dropzone-preview-grid';
        dropzone.appendChild(previewGrid);

        // Insert dropzone before the inline table
        var tabular = inlineGroup.querySelector('.tabular');
        if (tabular) {
            inlineGroup.insertBefore(dropzone, tabular);
        } else {
            inlineGroup.insertBefore(dropzone, inlineGroup.firstChild.nextSibling);
        }

        // Click to select files
        dropzone.addEventListener('click', function(e) {
            if (e.target.closest('.remove-preview')) return;
            fileInput.click();
        });

        // Drag events
        ['dragenter', 'dragover'].forEach(function(evt) {
            dropzone.addEventListener(evt, function(e) {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add('dragover');
            });
        });
        ['dragleave', 'drop'].forEach(function(evt) {
            dropzone.addEventListener(evt, function(e) {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove('dragover');
            });
        });

        dropzone.addEventListener('drop', function(e) {
            var files = e.dataTransfer.files;
            handleFiles(files, inlineGroup, previewGrid);
        });

        fileInput.addEventListener('change', function() {
            handleFiles(fileInput.files, inlineGroup, previewGrid);
            fileInput.value = '';
        });
    }

    function handleFiles(files, inlineGroup, previewGrid) {
        for (var i = 0; i < files.length; i++) {
            addFileToInline(files[i], inlineGroup, previewGrid);
        }
    }

    function addFileToInline(file, inlineGroup, previewGrid) {
        var isVideo = file.type.startsWith('video/');
        var isImage = file.type.startsWith('image/');
        if (!isImage && !isVideo) return;

        // Click the "Add another" link to create a new inline row
        var addBtn = inlineGroup.querySelector('.add-row a');
        if (addBtn) addBtn.click();

        // Find the last added inline row
        var rows = inlineGroup.querySelectorAll('.dynamic-media, .form-row:not(.empty-form), tr.form-row, .inline-related:not(.empty-form)');
        var lastRow = rows[rows.length - 1];
        if (!lastRow) return;

        // Set media type
        var typeSelect = lastRow.querySelector('[name$="-media_type"]');
        if (typeSelect) {
            typeSelect.value = isVideo ? 'video' : 'photo';
        }

        // Set the file on the appropriate input
        var fieldName = isVideo ? '-video_file' : '-image';
        var fileInputTarget = lastRow.querySelector('input[type="file"][name$="' + fieldName + '"]');
        if (fileInputTarget) {
            var dt = new DataTransfer();
            dt.items.add(file);
            fileInputTarget.files = dt.files;
            // Trigger change event
            fileInputTarget.dispatchEvent(new Event('change', { bubbles: true }));
        }

        // Show preview
        var previewItem = document.createElement('div');
        previewItem.className = 'dropzone-preview-item';

        if (isImage) {
            var img = document.createElement('img');
            img.src = URL.createObjectURL(file);
            previewItem.appendChild(img);
        } else {
            var vid = document.createElement('video');
            vid.src = URL.createObjectURL(file);
            vid.muted = true;
            previewItem.appendChild(vid);
        }

        var removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'remove-preview';
        removeBtn.textContent = '\u00d7';
        removeBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            // Check the DELETE checkbox on the corresponding inline row
            var deleteCheck = lastRow.querySelector('input[name$="-DELETE"]');
            if (deleteCheck) deleteCheck.checked = true;
            // Hide the row
            lastRow.style.display = 'none';
            previewItem.remove();
        });
        previewItem.appendChild(removeBtn);
        previewGrid.appendChild(previewItem);
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDropzone);
    } else {
        initDropzone();
    }
})();
