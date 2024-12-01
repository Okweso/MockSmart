import logo from './logo.svg';
import './App.css';
import React from 'react';
import {BrowserRouter, Routes, Route} from "react-router-dom";
import Layout from './pages/Layout';
import Home from './pages/Home';
import About from './pages/About';
import Contacts from './pages/Contacts';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <BrowserRouter>
      <Routes>
          <Route path='/' element={<Layout />}>
            <Route index element={<Home />}></Route>
            <Route path='About' element={<About />}></Route>
            <Route path='Contacts' element={<Contacts />}></Route>
            <Route path='Dashboard' element={<Dashboard/>} />
          </Route>
      </Routes>
    </BrowserRouter>
    
  );
}

export default App;
