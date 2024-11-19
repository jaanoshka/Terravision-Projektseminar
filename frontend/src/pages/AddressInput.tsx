import img1 from "../assets/img1.png";
import { useNavigate } from "react-router-dom";
import React, { ChangeEvent, useState } from "react";

const AddressInput = () => {
  const navigate = useNavigate();
  const [address, setAddress] = useState<string>("");

  async function processStep(e: React.MouseEvent) {
    console.log("HEllo");
    console.log(address);
    const response = await fetch(`http://localhost:4000/mesh/image/${address}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
    });
    console.log(response);
    navigate("/Step2", { state: { address: address } });
  }

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        height: "100vh", // Full viewport height
        backgroundImage: `url(${img1})`, // Full-screen background
        backgroundSize: "cover",
        backgroundPosition: "center 33%", // Adjust vertical alignment (lowered image)
      }}
    >
      <div
        style={{
          textAlign: "center",
          background: "rgba(255, 255, 255, 0.8)", // Subtle white background for better readability
          padding: "30px",
          borderRadius: "20px",
          boxShadow: "0px 4px 15px rgba(0, 0, 0, 0.2)", // Soft 3D effect
        }}
      >
        <input
          placeholder="Examplestreet 1, 12345 Examplecity"
          type="text"
          value={address}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
            setAddress(e.target.value)
          }
          style={{
            width: "300px",
            padding: "10px 20px",
            fontSize: "16px",
            border: "none",
            borderRadius: "20px",
            boxShadow: "inset 0px 4px 8px rgba(0, 0, 0, 0.1)", // Soft inset shadow for 3D look
            outline: "none",
            marginBottom: "20px",
          }}
        />
        <br />
        <button
          onClick={processStep}
          style={{
            padding: "10px 20px",
            fontSize: "16px",
            borderRadius: "20px",
            backgroundColor: "#d3d3d3", // Apple-like grey
            border: "none",
            cursor: "pointer",
            boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.2)", // 3D effect
            transition: "all 0.2s ease",
          }}
          onMouseOver={(e) =>
            (e.currentTarget.style.backgroundColor = "#c0c0c0") // Slightly darker on hover
          }
          onMouseOut={(e) =>
            (e.currentTarget.style.backgroundColor = "#d3d3d3")
          }
        >
          Submit
        </button>
      </div>
    </div>
  );
};

export default AddressInput;
