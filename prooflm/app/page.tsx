"use client";

import { useEffect, useState } from "react";
import axios from "axios";

export default function Home() {
  const [messages, setMessages] = useState<MessageEvent<any>[]>([]);

  useEffect(() => {
    const eventSource = new EventSource("http://localhost:5000/");

    eventSource.onmessage = (e) => {
      setMessages((p) => [...p, e]);
    };

    return () => {
      eventSource.close();
    };
  }, []);

  return (
    <div className="flex-col border border-red-500 flex-grow">
      <h1 className="text-3xl font-bold underline">Messages:</h1>
      <li>
        {messages.map((m, i) => (
          <ul key={i}>{JSON.stringify(m)}</ul>
        ))}
      </li>
    </div>
  );
}
