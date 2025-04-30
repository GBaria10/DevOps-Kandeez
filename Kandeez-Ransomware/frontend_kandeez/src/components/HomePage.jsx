import React from "react";
import "../styles/HomePage.css";

const HomePage = ({ onContinue }) => {
  return (
    <div className="homepage-body">
      <div className="dragon-container">
        <svg className="dragon-img" viewBox="0 0 1200 800" xmlns="http://www.w3.org/2000/svg">
          <path fill="#ff0000" d="M600,100 C750,100 800,200 900,250 C950,275 980,270 1000,300 C1020,330 1010,370 980,400 C950,430 900,440 870,430 C840,420 820,400 800,380 C780,360 750,350 730,370 C710,390 730,420 760,430 C790,440 820,430 840,400 C860,370 900,350 940,380 C980,410 1000,460 990,500 C980,540 950,570 900,580 C850,590 800,570 770,540 C740,510 720,470 670,450 C620,430 570,440 540,480 C510,520 520,570 550,600 C580,630 620,640 660,630 C700,620 730,590 740,550" />
        </svg>
      </div>

      <div className="red-glow"></div>

      <div className="container">
        <h1 className="title">Kandeez-Ransomware</h1>
        <p className="description">Your files have been encrypted. Pay the ransom to get the decryption key.</p>
        <button className="button" onClick={onContinue}>Pay Ransom</button>
      </div>
    </div>
  );
};

export default HomePage;
