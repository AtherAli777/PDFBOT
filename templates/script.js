async function search(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const query = formData.get('query');

    if (!query.trim()) {
        // The query is empty, do not make a request
        return;
    }

    try {
        const response = await fetch('/search', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        const resultDiv = document.querySelector('#result');
        resultDiv.textContent = data.result;
    } catch (error) {
        console.error(error);
        const resultDiv = document.querySelector('#result');
        resultDiv.textContent = 'An error occurred while searching. Please try again later.';
    }
}