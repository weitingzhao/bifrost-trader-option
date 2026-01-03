const mongoose = require('mongoose');
mongoose.set('strictQuery', false);
const dotenv = require('dotenv');
dotenv.config({ path: "./config.env" });
var app = require('express')();
var express = require('express');
var path = require('path');
var http = require('http').Server(app);

// import Router file
var pageRouter = require('./routes/routes');
var user = require("./models/UserModel");

var session = require('express-session');
var bodyParser = require('body-parser');
var flash = require('connect-flash');
var i18n = require("i18n-express");
var urlencodeParser = bodyParser.urlencoded({ extended: true });
app.use(urlencodeParser);
app.use(session({ resave: false, saveUninitialized: true, secret: 'nodedemo' }));
app.use(flash());

/* ---------for Local database connection---------- */
const DB = process.env.DATABASE_LOCAL;
if (DB) {
    mongoose.connect(DB, {
        useNewUrlParser: true
    }).then((con) => console.log("DB connection successfully..!"))
        .catch((err) => {
            console.log("⚠️  MongoDB connection failed (OK for UI viewing):", err.message);
            console.log("   Theme will still work for design reference");
        });
} else {
    console.log("⚠️  DATABASE_LOCAL not set - skipping MongoDB connection");
    console.log("   Theme will still work for design reference");
}

// for i18 usr
app.use(i18n({
    translationsPath: path.join(__dirname, 'i18n'), // <--- use here. Specify translations files path.
    siteLangs: ["es", "en", "fr", "ru", "it", "gr", "sp"],
    textsVarName: 'translation'
}));
app.use(express.static(__dirname + '/public'));

app.use('/public', express.static('public'));
app.set('layout', 'layouts/layout');
var expressLayouts = require('express-ejs-layouts');
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');
app.use(expressLayouts);

// Define All Route 
pageRouter(app);

app.all('*', function (req, res) {
    res.locals = { title: 'Error 500' };
    res.render('auth/auth-500', { layout: "layouts/layout-without-nav" });
});

http.listen(process.env.PORT, () => console.log(`Server running on port ${process.env.PORT}`));