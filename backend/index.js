const app = require('./app.js');

const PORT = 4002;

app.listen(PORT, "localhost", () => {
    console.log(`Server is running on port ${PORT}`);
})
  