const express = require('express');
const path = require('path');
const { exec } = require('child_process');

const app = express();
const port = 88; // Change port to 80

// Serve static files from the 'public' directory
app.use(express.static('public'));

// Endpoint to check if a systemd process is running
app.get('/check-process', (req, res) => {
    const processName = req.query.name;

    // Use systemd command to check if the process is running
    exec(`systemctl is-active ${processName}`, (error, stdout) => {
        if (error) {
            res.json({ isRunning: false });
        } else {
            res.json({ isRunning: stdout.trim() === 'active' });
        }
    });
});

// New endpoint to get a list of what is running
app.get('/get-running-list', (req, res) => {
    // You can customize this list based on your requirements
    const runningList = [
        'subvideo.service is running',
        'subimu.service is running',
        'subcontrol.service is running',
        'subsensor.service is running',
        'subhealth.service is running',
        'subweb.service is running',
        // Add more services as needed
    ];

    res.json({ runningList });
});

// Route to serve the index.html file
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start the server
app.listen(port, () => {
    console.log(`Server listening at http://localhost:${port}`);
});
