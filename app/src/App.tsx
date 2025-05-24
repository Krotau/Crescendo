import { useRef } from 'react';

import './App.css';
import Chat from './components/chat'
import ChatLog from './components/chat_log';
import Context from './components/context';
import { useAtom } from 'jotai';
import { fileMenuAtom } from './components/atoms';


const App = () => {

  let [open, setOpen] = useAtom(fileMenuAtom);

  let overlay_bg_class = `overlay_background ${open ? "open_bg" : "closed"}`
  let overlay_class = `overlay ${open ? "open_menu" : "closed"}`

  const modalRef = useRef(null);

  return (
    <>

    <div ref={modalRef} className={overlay_bg_class} onClick={(event) => {
      if (event.target !== modalRef.current) {
          return;
      }
      setOpen(!open);
    }}
      >
      <div className={overlay_class}>
        <div className={open ? "show" : "hide"}>
          <button onClick={() => {setOpen(!open)}}>Close</button>
          <button>File 1</button>
          <button>File 2</button>
          <button>File 3</button>
          <button>File 4</button>
        </div>
      </div>
    </div>

    <div className="chat_bg">

      <Chat />

      <ChatLog />

    </div>

    <div className="server_info_bg">

        <Context />
    
    </div>

    </>
  );
};

export default App;
