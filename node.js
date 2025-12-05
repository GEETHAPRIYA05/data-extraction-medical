const express = require('express');
const app = express();
const PORT = 3000;

app.get('/', (req, res) => {
    res.send('Hello, Medical History App!');
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
