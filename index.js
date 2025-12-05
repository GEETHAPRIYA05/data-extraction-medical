const express = require('express');
const app = express();
const PORT = 3000;

// Simple route
app.get('/', (req, res) => {
    res.send('Hello, Medical History App!');
});

// Start server with console log
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
