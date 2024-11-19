import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { BrowserRouter } from 'react-router-dom';
import "bootstrap/dist/css/bootstrap.css";
import ".";
import "./App.css";
import "./nav.css";

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);

root.render(
    <App />
);
