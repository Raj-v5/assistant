document.getElementById('speakButton').addEventListener('click', function() {
    const command = document.getElementById('commandInput').value;
    if (command) {
        // Replace with a function to send the command to your backend
        sendCommandToAssistant(command);
    }
});

document.getElementById('sendButton').addEventListener('click', function() {
    const command = document.getElementById('commandInput').value;
    if (command) {
        // Replace with a function to send the command to your backend
        sendCommandToAssistant(command);
    }
});

// Mock function to simulate sending command to backend and getting a response
function sendCommandToAssistant(command) {
    // Simulating an API call
    setTimeout(() => {
        const response = `You asked: ${command}. (This is a simulated response.)`;
        document.getElementById('responseOutput').textContent = response;
    }, 1000);
}
function sendCommandToAssistant(command) {
    fetch('/send_command', {  // This should match the route in your Flask app
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ command: command }),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('responseOutput').textContent = data.response;
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

document.getElementById('sendButton').addEventListener('click', function() {
    const commandInput = document.getElementById('commandInput');
    const command = commandInput.value;

    if (command) {
        // Send command to the Flask server
        fetch('/run_command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command: command })
        })
        .then(response => response.json())
        .then(data => {
            // Display the response in the responseOutput paragraph
            document.getElementById('responseOutput').innerText = data.response;
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
});
