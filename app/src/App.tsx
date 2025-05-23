import './App.css';
import Chat from './components/chat'
import ChatLog from './components/chat_log';
import Context from './components/context';


const App = () => {
  return (
    <>

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
