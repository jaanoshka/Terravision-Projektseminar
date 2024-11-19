import * as React from "react";

function Nav1(): JSX.Element {
  return (
    <nav className="nav">
      <a href="/" className="site-title">
        HOME
      </a>
      <ul>
        <li>
          <a href="/Step1">Address Input</a>

        </li>
      </ul>
    </nav>
  );
}

export default Nav1;
