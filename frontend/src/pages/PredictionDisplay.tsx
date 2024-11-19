import { useNavigate, useLocation } from "react-router-dom";
import React, { useEffect, useState } from "react";
import img1 from "../assets/img1.png";

const PredictionDisplay = () => {
  const [image, setImage] = useState<string>("");
  const [depth, setDepth] = useState<string>("");

  const navigate = useNavigate();
  const location = useLocation();
  const address = location.state.address;
  const model = location.state.model;

  useEffect(() => {
    fetch(`http://localhost:4000/mesh/image/${address}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
    })
      .then((res) => res.blob())
      .then((blob) => {
        setImage(URL.createObjectURL(blob));
      });
  }, []);

  useEffect(() => {
    fetch(`http://localhost:4000/mesh/depth/${address}/${model}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
    })
      .then((res) => res.blob())
      .then((blob) => {
        setDepth(URL.createObjectURL(blob));
      });
  }, []);

  function processStep(e: React.MouseEvent) {
    navigate("/Step4", { state: { model: model, address: address } });
  }

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "30% 70%",
        height: "100vh",
        backgroundImage: `url(${img1})`,
        backgroundSize: "cover",
        backgroundPosition: "center 33%",
        margin: "0",
      }}
    >
      {/* Sidebar */}
      <div
        style={{
          background: "rgba(255, 255, 255, 0.8)",
          padding: "20px",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <table style={{ width: "100%", marginBottom: "20px", textAlign: "center" }}>
          <tbody>
            <tr>
              <td style={{ textAlign: "left" }}>Address</td>
              <td style={{ textAlign: "right" }}>{address}</td>
            </tr>
            <br></br>
            <tr>
              <td style={{ textAlign: "left" }}>Model</td>
              <td style={{ textAlign: "right" }}>{model}</td>
            </tr>
          </tbody>
        </table>
        <br></br>
        <button
          onClick={processStep}
          style={{
            marginTop: "10px",
            padding: "10px 20px",
            fontSize: "16px",
            borderRadius: "20px",
            backgroundColor: "#d3d3d3",
            border: "none",
            cursor: "pointer",
          }}
        >
          Show 3D Model
        </button>
      </div>

      {/* Main Content */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-around",
          alignItems: "center",
        }}
      >
        {/* Satellite Image */}
        <div
          style={{
            width: "450px",
            height: "450px",
            border: "20px solid rgba(255, 255, 255, 0.1)",
            borderRadius: "20px",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            background: "rgba(255, 255, 255, 0.7)",
          }}
        >
          {image ? (
            <img
              src={image}
              alt="Satellite Image"
              style={{
                maxWidth: "100%",
                maxHeight: "100%",
                objectFit: "cover",
                borderRadius: "13px",
              }}
            />
          ) : (
            <p>Loading satellite image...</p>
          )}
        </div>

        {/* Depth Map */}
        <div
          style={{
            position: "relative",
            width: "450px",
            height: "450px",
            border: "20px solid rgba(255, 255, 255, 0.003)",
            borderRadius: "20px",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            background: "rgba(255, 255, 255, 0.711)",
          }}
        >
          {depth ? (
            <>
              <img
                src={depth}
                alt="Depth Map"
                style={{
                  maxWidth: "100%",
                  maxHeight: "100%",
                  objectFit: "cover",
                  borderRadius: "15px",
                }}
              />
              <a
                href={depth}
                download="depth_map.jpg"
                style={{
                  position: "absolute",
                  bottom: "10px",
                  right: "10px",
                  width: "30px",
                  height: "30px",
                  backgroundColor: "rgba(255, 255, 255, 0.8)",
                  borderRadius: "50%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  textDecoration: "none",
                  boxShadow: "0px 2px 4px rgba(0, 0, 0, 0.2)",
                }}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  style={{
                    width: "15px",
                    height: "15px",
                    color: "#007bff",
                  }}
                >
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="7 10 12 15 17 10" />
                  <line x1="12" y1="15" x2="12" y2="3" />
                </svg>
              </a>
            </>
          ) : (
            <p>Loading depth map...</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default PredictionDisplay;
