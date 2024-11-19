import "./App.css"; 
import NavBar from "./components/NAV";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import AddressInput from "./pages/AddressInput";
import ShowAerialImage from "./pages/ShowAerialImage";
import Mesh from "./pages/Mesh";
import PredictionDisplay from "./pages/PredictionDisplay"
import { createRoot } from 'react-dom/client'
import { Canvas } from '@react-three/fiber'

function App() {

  return (
    <Router>
      <NavBar />
      <Routes>
        <Route path="/Step2" element={<ShowAerialImage/>}/>
        <Route path="/Step3" element={<PredictionDisplay/>}/>
        <Route path="/Step4" element={<Mesh/>}/>
        <Route path="*" element={<AddressInput />}/>     
      </Routes>
    </Router>
  );
}

export default App;
