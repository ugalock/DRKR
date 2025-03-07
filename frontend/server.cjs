const express = require('express');
const expressStaticGzip = require('express-static-gzip');
const path = require('path');

const app = express();
const port = 3000;

// Serve compressed files
app.use('/', expressStaticGzip(path.join(__dirname, 'dist'), {
    enableBrotli: true,
    orderPreference: ['br'],
    serveStatic: {
        maxAge: '1y',
        cacheControl: true
    }
}));

// Fallback for SPA routing
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});