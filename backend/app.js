const express = require("express");
const app = express();
// const session = require('express-session');
const cors = require("cors");
// const crypto = require("crypto");



//global middleware

app.use(express.json());
app.use(express.urlencoded({ extended: true })); 
app.use(express.static('public'));
app.use(cors()); // allow http requests from localhost

// const secret = crypto.randomBytes(16).toString('hex');

// app.use(session({
//     secret: secret,
//     resave: false,
//     saveUninitialized: false
// }))


// require modules

// const user = require("./routes/User");
// const auth = require("./routes/Auth");
// const busses = require("./routes/Busses");
// const appointments = require("./routes/Appointments");
// const destinations = require("./routes/Destinations");
// const requests = require("./routes/Requests");

const image = require("./routes/image");




// API routes (endpoints)

// app.use("/user",user)
// app.use("/auth", auth);
// app.use("/busses", busses);
// app.use("/appointments", appointments);
// app.use("/destinations", destinations);
// app.use("/requests", requests);

app.use("/convert", image);



module.exports = app;