
        document.querySelector('#submit_file').addEventListener('click', event => {
            handleImageUpload(event)
        })
        function handleImageUpload(e) {
            e.preventDefault();
            const file = document.getElementById('file_upload').files;
            const formData = new FormData();
            formData.append('file', file[0]);
            fetch('/api/image_upload', {
                method: 'POST',
                body: formData
            }).then(response => response.json())
            .then(data => console.log(data))
            .catch(error => console.log(error))
        }