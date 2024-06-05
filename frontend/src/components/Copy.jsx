import React, { useState, useEffect } from "react";
import { CopyToClipboard } from "react-copy-to-clipboard";
import { MdContentCopy } from "react-icons/md";
import "../App.css";

export default function Copy({ text }) {
  const [value, setValue] = useState("Try copy this :) Button UI will change!");
  const [isCopied, setCopied] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    setValue(text);
    const timeout = setTimeout(() => {
      setMessage("");
    }, 3000);

    return () => clearTimeout(timeout);
  }, [text]);

  return (
    <div>
      <p className="textbox">
        {value}
        <div role="button" tabIndex={0}>
          <CopyToClipboard text={text} onCopy={() => {
            setCopied(true);
            setMessage("Copied!");
          }}>
            <MdContentCopy
              onClick={() => {
                setCopied(true);
                setMessage("Copied");
              }}
              style={{ cursor: "pointer" }}
            />
          </CopyToClipboard>
          {message && <span>{message}</span>}
        </div>
      </p>
    </div>
  );
}
