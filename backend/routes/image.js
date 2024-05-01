const multer = require('multer');

const router = require("express").Router();
const upload = multer({ dest: '../uploads' });

// Route for handling image conversion
router.post('/',upload.single('image'), async (req, res) => {
  try {
    // Just send "Hello, world!" as the response
    res.status(200).json({ text: "Hello, world!" });
  } catch (error) {
    console.error('Error occurred:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
