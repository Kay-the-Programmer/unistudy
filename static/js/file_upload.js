document.addEventListener('DOMContentLoaded', function () {
    const dropZone = document.getElementById('dropZone');
    // The actual file input is rendered by Django form, find it by its ID or name.
    // Let's assume `form.file.id_for_label` in template makes its ID `id_file` if name is `file`.
    // Or more robustly, find it by name if the ID is unpredictable.
    // For `{{ form.file.as_hidden }}`, Django usually gives it `id_id_file` if field name is `file`.
    // Let's try to find it based on the name attribute if `as_hidden` doesn't give a predictable ID.
    // The `MaterialUploadForm` has `file = forms.FileField(...)`. So name is 'file'.
    const fileInput = document.querySelector('input[type="file"][name="file"]');
    const fileFeedback = document.getElementById('fileFeedback');
    const titleInput = document.querySelector('input[type="text"][name="title"]'); // Assuming title field name is 'title'

    if (!dropZone || !fileInput || !fileFeedback) {
        console.warn('File upload enhancement: Drop zone or file input or feedback element not found.');
        return;
    }

    // Make the dropZone clickable to trigger the hidden file input
    dropZone.addEventListener('click', function () {
        fileInput.click();
    });

    // Handle file selection via click
    fileInput.addEventListener('change', function () {
        if (fileInput.files.length > 0) {
            handleFile(fileInput.files[0]);
        } else {
            fileFeedback.textContent = ''; // Clear feedback if no file selected
        }
    });

    // Drag over
    dropZone.addEventListener('dragover', function (event) {
        event.preventDefault(); // Necessary to allow drop
        dropZone.classList.add('dragover');
    });

    // Drag leave
    dropZone.addEventListener('dragleave', function (event) {
        dropZone.classList.remove('dragover');
    });

    // Drop
    dropZone.addEventListener('drop', function (event) {
        event.preventDefault();
        dropZone.classList.remove('dragover');

        if (event.dataTransfer.files.length > 0) {
            const droppedFile = event.dataTransfer.files[0];
            // Set the dropped file to the hidden file input
            // Note: For security reasons, browsers might not allow setting FileList directly.
            // However, assigning to .files usually works for a single file if input is empty.
            // If multiple files were allowed, one would create a new FileList.
            // For a single file, this should be fine.
            try {
                 fileInput.files = event.dataTransfer.files; // Assign the FileList
            } catch (e) {
                // Some browsers might throw error here.
                // As a fallback, we might not be able to directly assign.
                // However, modern browsers are generally okay with this.
                console.error("Error assigning files to input: ", e);
                fileFeedback.textContent = 'Error processing dropped file. Please use the fallback input.';
                return;
            }

            handleFile(droppedFile);
        }
    });

    function handleFile(file) {
        fileFeedback.textContent = `Selected file: ${file.name}`;
        // Auto-populate title if title field exists and is empty
        if (titleInput && titleInput.value.trim() === '') {
            const filenameWithoutExtension = file.name.substring(0, file.name.lastIndexOf('.')) || file.name;
            // Basic sanitization: replace underscores/hyphens with spaces, capitalize words
            let autoTitle = filenameWithoutExtension.replace(/[_-]/g, ' ');
            // Capitalize first letter of each word
            autoTitle = autoTitle.toLowerCase().split(' ').map(s => s.charAt(0).toUpperCase() + s.substring(1)).join(' ');
            titleInput.value = autoTitle;
        }

        // Optionally, trigger change event on file input if other scripts depend on it
        // const changeEvent = new Event('change', { bubbles: true });
        // fileInput.dispatchEvent(changeEvent);
    }
});
