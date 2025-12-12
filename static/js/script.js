document.addEventListener('DOMContentLoaded', function() {
    // Initialize Materialize components
    M.AutoInit();

    // Get DOM elements
    const keysFileInput = document.getElementById('keys-file');
    const uploadKeysBtn = document.getElementById('upload-keys-btn');
    const nszFileInput = document.getElementById('nsz-file');
    const convertBtn = document.getElementById('convert-btn');
    const convertAllBtn = document.getElementById('convert-all-btn');

    const keysResultDiv = document.getElementById('keys-upload-result');
    const conversionResultDiv = document.getElementById('conversion-result');
    const downloadSection = document.getElementById('download-section');
    const filesSection = document.getElementById('files-section');

    // Check if keys file is already uploaded
    function checkKeysStatus() {
        fetch('/keys-status')
        .then(response => response.json())
        .then(data => {
            if (data.keys_uploaded) {
                keysResultDiv.innerHTML = '<div class="status-message success-message">Keys file is already uploaded and ready for use!</div>';
            } else {
                keysResultDiv.innerHTML = '<div class="status-message error-message">Please upload your prod.keys file first</div>';
            }
        })
        .catch(error => {
            console.error('Error checking keys status:', error);
        });
    }

    // Upload keys functionality
    uploadKeysBtn.addEventListener('click', function() {
        const file = keysFileInput.files[0];
        if (!file) {
            showMessage(keysResultDiv, 'Please select a keys file first.', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        // Show loading state
        uploadKeysBtn.classList.add('loading');
        uploadKeysBtn.disabled = true;

        fetch('/upload-keys/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showMessage(keysResultDiv, data.message, 'success');
                checkKeysStatus();  // Update status after upload
            } else {
                showMessage(keysResultDiv, 'Unexpected response from server', 'error');
            }
        })
        .catch(error => {
            showMessage(keysResultDiv, `Error uploading keys: ${error}`, 'error');
        })
        .finally(() => {
            // Reset loading state
            uploadKeysBtn.classList.remove('loading');
            uploadKeysBtn.disabled = false;
        });
    });

    // Convert NSZ to NSP functionality - single file
    convertBtn.addEventListener('click', function() {
        const files = nszFileInput.files;
        if (!files || files.length === 0) {
            showMessage(conversionResultDiv, 'Please select one or more NSZ files first.', 'error');
            return;
        }

        // First check if keys are available
        fetch('/keys-status')
        .then(response => response.json())
        .then(data => {
            if (!data.keys_uploaded) {
                showMessage(conversionResultDiv, 'Please upload your prod.keys file first.', 'error');
                return;
            }

            // Check file existence before upload
            checkFileExistence(Array.from(files), function(existingFiles) {
                if (existingFiles.length > 0) {
                    if (!confirm(`The following files already exist: ${existingFiles.join(', ')}\nDo you want to skip these files and continue with the others?`)) {
                        return;
                    }
                }

                if (files.length === 1) {
                    // Single file conversion
                    singleFileConversion(files[0]);
                } else {
                    // Multiple file conversion
                    multipleFileConversion(files);
                }
            });
        })
        .catch(error => {
            showMessage(conversionResultDiv, `Error checking keys status: ${error}`, 'error');
        });
    });

    // Function to check if files exist on the server
    function checkFileExistence(files, callback) {
        // Get list of existing files to compare
        fetch('/files')
        .then(response => response.json())
        .then(data => {
            const existingFiles = [];
            const uploadedFiles = data.nsz_files || [];

            files.forEach(file => {
                if (uploadedFiles.includes(file.name)) {
                    existingFiles.push(file.name);
                }
            });

            callback(existingFiles);
        })
        .catch(error => {
            console.error('Error checking file existence:', error);
            // If we can't check, proceed anyway
            callback([]);
        });
    }

    // Function to handle single file conversion
    function singleFileConversion(file) {
        const formData = new FormData();
        formData.append('file', file);

        // Show loading state
        convertBtn.classList.add('loading');
        convertBtn.disabled = true;

        fetch('/convert-nsz/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.message && data.filename) {
                showMessage(conversionResultDiv, data.message, 'success');

                // Refresh downloadable files
                refreshDownloadableFiles();
                refreshFilesSection();
            } else if (data.message && data.message.includes("already exists")) {
                // Handle file already exists case
                showMessage(conversionResultDiv, data.message, 'info');
                refreshFilesSection();
            } else {
                showMessage(conversionResultDiv, 'Unexpected response from server', 'error');
            }
        })
        .catch(error => {
            showMessage(conversionResultDiv, `Error during conversion: ${error}`, 'error');
        })
        .finally(() => {
            // Reset loading state
            convertBtn.classList.remove('loading');
            convertBtn.disabled = false;
        });
    }

    // Function to handle multiple file conversion
    function multipleFileConversion(files) {
        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }

        // Show loading state
        convertBtn.classList.add('loading');
        convertBtn.disabled = true;

        fetch('/convert-nsz-multi/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showMessage(conversionResultDiv, data.message, 'success');

                // Show detailed results
                if (data.results) {
                    let resultDetails = '<ul style="margin-top: 10px;">';
                    data.results.forEach(result => {
                        let statusClass = 'info-message';
                        if (result.status === 'success') statusClass = 'success-message';
                        else if (result.status === 'error') statusClass = 'error-message';
                        else if (result.status === 'skipped') statusClass = 'info-message';

                        let statusText = result.status;
                        if (result.status === 'skipped') {
                            statusText = 'skipped (already exists)';
                        }

                        resultDetails += `<li class="${statusClass}">${result.filename}: ${statusText} ${result.error ? `(${result.error})` : ''} ${result.message ? `(${result.message})` : ''}</li>`;
                    });
                    resultDetails += '</ul>';
                    conversionResultDiv.innerHTML += resultDetails;
                }

                // Refresh downloadable files
                refreshDownloadableFiles();
                refreshFilesSection();
            } else {
                showMessage(conversionResultDiv, 'Unexpected response from server', 'error');
            }
        })
        .catch(error => {
            showMessage(conversionResultDiv, `Error during conversion: ${error}`, 'error');
        })
        .finally(() => {
            // Reset loading state
            convertBtn.classList.remove('loading');
            convertBtn.disabled = false;
        });
    }

    // Convert all NSZ files in directory
    convertAllBtn.addEventListener('click', function() {
        // First check if keys are available
        fetch('/keys-status')
        .then(response => response.json())
        .then(data => {
            if (!data.keys_uploaded) {
                showMessage(conversionResultDiv, 'Please upload your prod.keys file first.', 'error');
                return;
            }

            // Show loading state
            convertAllBtn.classList.add('loading');
            convertAllBtn.disabled = true;

            fetch('/convert-directory/', {
                method: 'POST',
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    showMessage(conversionResultDiv, data.message, 'success');

                    // Show detailed results
                    if (data.results) {
                        let resultDetails = '<ul style="margin-top: 10px;">';
                        data.results.forEach(result => {
                            let statusClass = 'info-message';
                            if (result.status === 'success') statusClass = 'success-message';
                            else if (result.status === 'error') statusClass = 'error-message';

                            resultDetails += `<li class="${statusClass}">${result.filename}: ${result.status} ${result.error ? `(${result.error})` : ''}</li>`;
                        });
                        resultDetails += '</ul>';
                        conversionResultDiv.innerHTML += resultDetails;
                    }

                    // Refresh downloadable files
                    refreshDownloadableFiles();
                    refreshFilesSection();
                } else {
                    showMessage(conversionResultDiv, 'Unexpected response from server', 'error');
                }
            })
            .catch(error => {
                showMessage(conversionResultDiv, `Error during directory conversion: ${error}`, 'error');
            })
            .finally(() => {
                // Reset loading state
                convertAllBtn.classList.remove('loading');
                convertAllBtn.disabled = false;
            });
        })
        .catch(error => {
            showMessage(conversionResultDiv, `Error checking keys status: ${error}`, 'error');
        });
    });

    // Function to show messages
    function showMessage(element, message, type) {
        element.innerHTML = `<div class="status-message ${type}-message">${message}</div>`;
    }

    // Function to refresh downloadable files
    function refreshDownloadableFiles() {
        fetch('/uploaded-files')
        .then(response => response.json())
        .then(data => {
            const nspFiles = data.nsp_files || [];

            if (nspFiles.length > 0) {
                let html = '<ul>';
                nspFiles.forEach(file => {
                    html += `
                    <li>
                        <a href="/download/${file}" class="waves-effect waves-light btn">
                            Download ${file}
                            <i class="material-icons right">file_download</i>
                        </a>
                    </li>`;
                });
                html += '</ul>';
                downloadSection.innerHTML = html;
            } else {
                downloadSection.innerHTML = '<p>No converted files available yet.</p>';
            }
        })
        .catch(error => {
            console.error('Error fetching uploaded files:', error);
        });
    }

    // Function to refresh files section
    function refreshFilesSection() {
        fetch('/files')
        .then(response => response.json())
        .then(data => {
            let html = '';

            if (data.nsz_files.length > 0) {
                html += '<h5>NSZ Files</h5><ul>';
                data.nsz_files.forEach(file => {
                    html += `<li><i class="material-icons tiny">insert_drive_file</i> ${file}</li>`;
                });
                html += '</ul>';
            } else {
                html = '<p>No NSZ files available.</p>';
            }

            filesSection.innerHTML = html;
        })
        .catch(error => {
            console.error('Error fetching files:', error);
            filesSection.innerHTML = '<p>Error loading files.</p>';
        });
    }

    // Add event listener for clean output button
    const cleanOutputBtn = document.getElementById('clean-output-btn');
    const cleanOutputResult = document.getElementById('clean-output-result');
    const cleanUploadsBtn = document.getElementById('clean-uploads-btn');
    const cleanUploadsResult = document.getElementById('clean-uploads-result');
    const cleanAllBtn = document.getElementById('clean-all-btn');
    const cleanAllResult = document.getElementById('clean-all-result');

    cleanOutputBtn.addEventListener('click', function() {
        if (!confirm('Are you sure you want to delete all NSP files in the output folder? This action cannot be undone.')) {
            return;
        }

        // Show loading state
        cleanOutputBtn.classList.add('loading');
        cleanOutputBtn.disabled = true;

        fetch('/clean-output/', {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showMessage(cleanOutputResult, data.message, 'success');
                refreshDownloadableFiles();  // Refresh the download section
                refreshFilesSection();  // Also refresh the file list
            } else {
                showMessage(cleanOutputResult, 'Unexpected response from server', 'error');
            }
        })
        .catch(error => {
            showMessage(cleanOutputResult, `Error cleaning output: ${error}`, 'error');
        })
        .finally(() => {
            // Reset loading state
            cleanOutputBtn.classList.remove('loading');
            cleanOutputBtn.disabled = false;
        });
    });

    // Add event listener for clean uploads button
    cleanUploadsBtn.addEventListener('click', function() {
        if (!confirm('Are you sure you want to delete all NSZ files in the uploads folder? This action cannot be undone.')) {
            return;
        }

        // Show loading state
        cleanUploadsBtn.classList.add('loading');
        cleanUploadsBtn.disabled = true;

        fetch('/clean-uploads/', {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showMessage(cleanUploadsResult, data.message, 'success');
                refreshFilesSection();  // Refresh the file list
            } else {
                showMessage(cleanUploadsResult, 'Unexpected response from server', 'error');
            }
        })
        .catch(error => {
            showMessage(cleanUploadsResult, `Error cleaning uploads: ${error}`, 'error');
        })
        .finally(() => {
            // Reset loading state
            cleanUploadsBtn.classList.remove('loading');
            cleanUploadsBtn.disabled = false;
        });
    });

    // Add event listener for clean all button
    cleanAllBtn.addEventListener('click', function() {
        if (!confirm('Are you sure you want to delete ALL files in both uploads and output folders? This action cannot be undone and will remove all NSZ and NSP files.')) {
            return;
        }

        // Show loading state
        cleanAllBtn.classList.add('loading');
        cleanAllBtn.disabled = true;

        fetch('/clean-all/', {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showMessage(cleanAllResult, data.message, 'success');
                refreshDownloadableFiles();  // Refresh the download section
                refreshFilesSection();  // Also refresh the file list
            } else {
                showMessage(cleanAllResult, 'Unexpected response from server', 'error');
            }
        })
        .catch(error => {
            showMessage(cleanAllResult, `Error cleaning all: ${error}`, 'error');
        })
        .finally(() => {
            // Reset loading state
            cleanAllBtn.classList.remove('loading');
            cleanAllBtn.disabled = false;
        });
    });

    // Load everything on initial load
    checkKeysStatus();
    refreshDownloadableFiles();
    refreshFilesSection();
});