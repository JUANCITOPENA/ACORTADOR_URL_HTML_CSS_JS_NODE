function shortenUrl() {
    const longUrl = document.getElementById('longUrl').value;

    if (longUrl) {
        fetch('/api/shorten', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ longUrl })
        }).then(response => response.json())
          .then(data => {
              document.getElementById('shortUrl').innerText = data.shortUrl;
              document.getElementById('visitButton').style.display = 'inline';
              document.getElementById('copyButton').style.display = 'inline';
              document.getElementById('visitButton').setAttribute('onclick', `openInNewTab('${data.shortUrl}')`);
          }).catch(error => {
              console.error('Error:', error);
              alert('Hubo un problema al acortar la URL.');
          });
    }
}

function copyToClipboard() {
    const shortUrl = document.getElementById('shortUrl').innerText;
    navigator.clipboard.writeText(shortUrl);
}

function openInNewTab(url) {
    window.open(url, '_blank').focus();
}

function clearForm() {
    document.getElementById('longUrl').value = '';
    document.getElementById('shortUrl').innerText = '';
    document.getElementById('visitButton').style.display = 'none';
    document.getElementById('copyButton').style.display = 'none';
}
