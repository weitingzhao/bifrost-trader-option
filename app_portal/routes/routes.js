const express = require('express');
const route = express.Router();

// Contorller
const AuthController = require("../controller/AuthController");

// const route = express.Router();
module.exports = function (route) {

    route.use((req, res, next) => {
        var uemail = req.session.useremail;
        const allowUrls = ["/login", "/auth-validate", "/register", "/signup", "/forgotpassword", "/sendforgotpasswordlink", "/resetpassword", "/error", "/changepassword"];
        if (allowUrls.indexOf(req.path) !== -1) {
            if (uemail != null && uemail != undefined) {
                return res.redirect('/');
            }

        } else if (!uemail) {
            return res.redirect('/login');
        }
        next();
    })
    route.get("/", function (req, res) {
        res.render("index");
    });

    route.get("/index", function (req, res) {
        res.render("index");
    });
 
    //email
    route.get('/auth-confirm-mail-2', function (req, res) {
        res.render('auth-confirm-mail-2', { layout: "layouts/layout-without-nav", });
    });
    //email
    route.get('/auth-confirm-mail', function (req, res) {
        res.render('auth-confirm-mail', { layout: "layouts/layout-without-nav", });
    });
    //email
    route.get('/auth-email-verification-2', function (req, res) {
        res.render('auth-email-verification-2', { layout: "layouts/layout-without-nav", });
    });
    //email
    route.get('/auth-email-verification', function (req, res) {
        res.render('auth-email-verification', { layout: "layouts/layout-without-nav", });
    });
    //lock screen
    route.get('/auth-lock-screen-2', function (req, res) {
        res.render('auth-lock-screen-2', { layout: "layouts/layout-without-nav", });
    });
    //lock screen
    route.get('/auth-lock-screen', function (req, res) {
        res.render('auth-lock-screen', { layout: "layouts/layout-without-nav", });
    });
    route.get('/auth-login-2', function (req, res) {
        res.render('auth-login-2', { layout: "layouts/layout-without-nav", });
    });
    route.get('/auth-login', function (req, res) {
        res.render('auth-login', { layout: "layouts/layout-without-nav", });
    });
    route.get('/auth-recoverpw-2', function (req, res) {
        res.render('auth-recoverpw-2', { layout: "layouts/layout-without-nav", });
    });
    route.get('/auth-recoverpw', function (req, res) {
        res.render('auth-recoverpw', { layout: "layouts/layout-without-nav", });
    });
    route.get('/auth-register-2', function (req, res) {
        res.render('auth-register-2', { layout: "layouts/layout-without-nav", });
    });
    route.get('/auth-register', function (req, res) {
        res.render('auth-register', { layout: "layouts/layout-without-nav", });
    });
    route.get('/auth-two-step-verification-2', function (req, res) {
        res.render('auth-two-step-verification-2', { layout: "layouts/layout-without-nav", });
    });
    route.get('/auth-two-step-verification', function (req, res) {
        res.render('auth-two-step-verification', { layout: "layouts/layout-without-nav", });
    });
    route.get('/pages-404', function (req, res) {
        res.render('pages-404', { layout: "layouts/layout-without-nav" });
    });
    route.get('/pages-500', function (req, res) {
        res.render('pages-500', { layout: "layouts/layout-without-nav" });
    });
    route.get('/pages-comingsoon', function (req, res) {
        res.render('pages-comingsoon', { layout: "layouts/layout-without-nav" });
    });
    route.get('/pages-maintenance', function (req, res) {
        res.render('pages-maintenance', { layout: "layouts/layout-without-nav" });
    });




    // layouts
    route.get('/layouts-boxed', function (req, res) {
        res.render('layouts-boxed', { layout: "layouts/layout-boxed", title: "Boxed Layout", page_title: 'Boxed Layout' });
    });
    route.get('/layouts-colored-sidebar', function (req, res) {
        res.render('layouts-colored-sidebar', { layout: "layouts/layout-colored-sidebar", title: "Colored Sidebar", page_title: 'Colored Sidebar' });
    });
    route.get('/layouts-compact-sidebar', function (req, res) {
        res.render('layouts-compact-sidebar', { layout: "layouts/layout-compact-sidebar", title: "Compact Sidebar", page_title: 'Compact Sidebar' });
    });
    // layouts-horizontal
    route.get('/layouts-hori-boxed-width', function (req, res) {
        res.render('layouts-hori-boxed-width', { layout: "layouts/layouts-hori-boxed-width", title: "Horizontal Layout", page_title: 'Horizontal Layout' });
    });
    route.get('/layouts-hori-colored-header', function (req, res) {
        res.render('layouts-hori-colored-header', { layout: "layouts/layouts-hori-colored-header", title: "Icon Sidebar", page_title: 'Icon Sidebar' });
    });
    route.get('/layouts-hori-preloader', function (req, res) {
        res.render('layouts-hori-preloader', { layout: "layouts/layouts-hori-preloader", title: "Light Sidebar", page_title: 'Light Sidebar' });
    });
    route.get('/layouts-hori-scrollable', function (req, res) {
        res.render('layouts-hori-scrollable', { layout: "layouts/layouts-hori-scrollable", title: "Light Sidebar", page_title: 'Light Sidebar' });
    });
    route.get('/layouts-hori-topbar-light', function (req, res) {
        res.render('layouts-hori-topbar-light', { layout: "layouts/layouts-hori-topbar-light", title: "Light Sidebar", page_title: 'Light Sidebar' });
    });
    route.get('/layouts-horizontal', function (req, res) {
        res.render('layouts-horizontal', { layout: "layouts/layout-horizontal", title: "Horizontal Layout", page_title: 'Horizontal Layout' });
    });
    route.get('/layouts-icon-sidebar', function (req, res) {
        res.render('layouts-icon-sidebar', { layout: "layouts/layouts-icon-sidebar", title: "Icon Sidebar", page_title: 'Icon Sidebar' });
    });
    route.get('/layouts-light-sidebar', function (req, res) {
        res.render('layouts-light-sidebar', { layout: "layouts/layouts-light-sidebar", title: "Light Sidebar", page_title: 'Light Sidebar' });
    });
    route.get('/layouts-preloader', function (req, res) {
        res.render('layouts-preloader', { layout: "layouts/layouts-preloader", title: "Light Sidebar", page_title: 'Light Sidebar' });
    });
    route.get('/layouts-scrollable', function (req, res) {
        res.render('layouts-scrollable', { layout: "layouts/layouts-scrollable", title: "Light Sidebar", page_title: 'Light Sidebar' });
    });


    // // Auth
    route.get('/login', (req, res, next) => {
        res.render('Auth/login', { title: 'Login', layout: 'layouts/layout-without-nav', 'message': req.flash('message'), error: req.flash('error') })
    })

    // validate login form
    route.post("/auth-validate", AuthController.validate)

    // logout
    route.get("/logout", AuthController.logout);

    route.get('/register', (req, res, next) => {
        res.render('Auth/register', { title: 'Register', layout: 'layouts/layout-without-nav', message: req.flash('message'), error: req.flash('error') })
    })

    // validate register form
    route.post("/signup", AuthController.signup)


    route.get('/forgotpassword', (req, res, next) => {
        res.render('auth/forgotpassword', { title: 'Forgot password', layout: 'layouts/layout-without-nav', message: req.flash('message'), error: req.flash('error') })
    })

    // send forgot password link on user email
    route.post("/sendforgotpasswordlink", AuthController.forgotpassword)

    // reset password
    route.get("/resetpassword", AuthController.resetpswdview);
    // Change password
    route.post("/changepassword", AuthController.changepassword);

    //500
    route.get('/error', (req, res, next) => {
        res.render('auth/auth-500', { title: '500 Error', layout: 'layouts/layout-without-nav' });
    })
}

