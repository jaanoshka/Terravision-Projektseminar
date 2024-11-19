import { useNavigate, useLocation } from "react-router-dom";
import React, { ChangeEvent, useState, useEffect } from "react";
import img1 from "../assets/img1.png";

const ShowAerialImage = () => {
  const [model, setModel] = useState<string>("Depth Anything V2");
  const [image, setImage] = useState<string>("");

  const navigate = useNavigate();
  const location = useLocation();
  const address = location.state.address;

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

  function processStep(e: React.MouseEvent) {
    navigate("/Step3", { state: { address: address, model: model } });
  }

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "30% 70%",
        alignItems: "center",
        height: "calc(100vh - 20px)", // Full viewport height minus 20px for top and bottom gaps
        backgroundImage: `url(${img1})`,
        backgroundSize: "cover",
        backgroundPosition: "center 33%", // Lower the background image slightly
      }}
    >
      {/* Sidebar (30%) */}
      <div
        style={{
          margin: "10px", // Maintain gap around the sidebar
          background: "rgba(255, 255, 255, 0.73)",
          padding: "20px",
          borderRadius: "20px",
          boxShadow: "0px 4px 15px rgba(0, 0, 0, 0.1)",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          height: "calc(100% - 20px)", // Leave gap above and below
        }}
      >
        <table style={{ width: "100%", borderSpacing: "10px" }}>
          <tbody>
            <tr>
              <td>Address:</td>
              <td style={{ textAlign: "right" }}>{address}</td>
            </tr>
            <br></br>
            <tr>
              <td>Model:</td>
              <td style={{ textAlign: "right" }}>
                <select
                  value={model}
                  onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                    setModel(e.target.value)
                  }
                  style={{
                    padding: "8px",
                    fontSize: "14px",
                    border: "none",
                    borderRadius: "10px",
                    background: "#f0f0f0",
                    boxShadow: "inset 0px 4px 8px rgba(0, 0, 0, 0.1)",
                  }}
                >
                  <option value="Depth Anything V2">Depth Anything V2</option>
                  <option value="Zoe Depth">Zoe Depth</option>
                  <option value="Unet Baseline">Baseline</option>
                </select>
              </td>
            </tr>
          </tbody>
        </table>
        <br></br>
        <button
          onClick={processStep}
          style={{
            marginTop: "20px",
            padding: "10px 20px",
            fontSize: "16px",
            borderRadius: "20px",
            backgroundColor: "#d3d3d3",
            border: "none",
            cursor: "pointer",
            boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.2)",
            transition: "all 0.2s ease",
          }}
          onMouseOver={(e) =>
            (e.currentTarget.style.backgroundColor = "#c0c0c0")
          }
          onMouseOut={(e) =>
            (e.currentTarget.style.backgroundColor = "#d3d3d3")
          }
        >
          Submit
        </button>
      </div>

      {/* Main Content (70%) */}
      <div
        style={{
          margin: "10px",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100%", // Take full grid height
          position: "relative", // Positioning for the image layout
        }}
      >
        {image ? (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
            }}
          >
            {/* Outer Frame */}
            <div
              style={{
                width: "650px", // Quadratic frame size
                height: "650px",
                border: "20px solid rgba(255, 255, 255, 0.63)", // Outer frame
                borderRadius: "40px",
                position: "relative",
                display: "inline-block",
              }}
            >
              {/* Translucent Image Frame */}
              <div
                style={{
                  width: "100%",
                  height: "100%",
                  background: "rgba(255, 255, 255, 0.78)",
                  borderRadius: "20px",
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  position: "relative",
                }}
              >
                <img
                  src={image}
                  alt="Satellite Image"
                  style={{
                    maxWidth: "100%",
                    maxHeight: "100%",
                    objectFit: "cover",
                    borderRadius: "10px",
                  }}
                />
                {/* Download Icon at the Bottom */}
                <a
                  href={image}
                  download="satellite_image.jpg"
                  style={{
                    position: "absolute",
                    bottom: "10px",
                    right: "10px",
                    width: "40px",
                    height: "40px",
                    backgroundColor: "rgba(255, 255, 255, 0.8)",
                    borderRadius: "50%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.2)",
                    textDecoration: "none",
                  }}
                  title="Download"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    style={{ width: "20px", height: "20px", color: "#007bff" }}
                  >
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="7 10 12 15 17 10" />
                    <line x1="12" y1="15" x2="12" y2="3" />
                  </svg>
                </a>
              </div>
            </div>
          </div>
        ) : (
          <p>Loading image...</p>
        )}
      </div>
    </div>
  );
};

export default ShowAerialImage;
