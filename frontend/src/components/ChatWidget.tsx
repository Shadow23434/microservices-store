import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { MessageCircle, X, Send, Sparkles, Star, Loader2, Bot } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import recommenderService from '../api/recommenderService';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  products?: any[];
  created_at?: string;
}

const WELCOME_MESSAGE: ChatMessage = {
  role: 'assistant',
  content:
    'Hello! 👋 I am the Store AI assistant. You can ask me about products, for example: "I want a laptop under $1600" or "Suggest self-help books". How can I help you today?',
};

export default function ChatWidget() {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME_MESSAGE]);
  const [input, setInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [hasLoadedHistory, setHasLoadedHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when new message arrives
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  // Load conversation history from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('chat_conversation_id');
    if (saved) {
      const id = Number(saved);
      setConversationId(id);
      // Load history from API
      recommenderService
        .getChatHistory(id)
        .then((res: any) => {
          if (res?.messages && Array.isArray(res.messages) && res.messages.length > 0) {
            setMessages([WELCOME_MESSAGE, ...res.messages]);
          }
          setHasLoadedHistory(true);
        })
        .catch(() => {
          setHasLoadedHistory(true);
        });
    } else {
      setHasLoadedHistory(true);
    }
  }, []);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isSending) return;

    const userMessage: ChatMessage = { role: 'user', content: trimmed };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsSending(true);

    try {
      const response = await recommenderService.sendChatMessage({
        message: trimmed,
        customer_id: user?.id || 1,
        session_id: `session_${user?.id || 'guest'}`,
      }) as any;

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response?.answer || 'Sorry, I cannot respond right now.',
        products: response?.products || [],
      };

      setMessages((prev) => [...prev, assistantMessage]);

      if (response?.conversation_id && response.conversation_id !== conversationId) {
        setConversationId(response.conversation_id);
        localStorage.setItem('chat_conversation_id', String(response.conversation_id));
      }
    } catch (err) {
      console.error('Chat error:', err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Rất tiếc, đã có lỗi xảy ra. Vui lòng thử lại sau.',
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  const handleQuickQuestion = (question: string) => {
    setInput(question);
    setTimeout(() => {
      const form = document.getElementById('chat-form') as HTMLFormElement;
      if (form) form.requestSubmit();
    }, 50);
  };

  const handleReset = () => {
    setMessages([WELCOME_MESSAGE]);
    setConversationId(null);
    localStorage.removeItem('chat_conversation_id');
  };

  return (
    <>
      {/* Floating Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-40 bg-indigo-600 hover:bg-indigo-700 text-white p-4 rounded-full shadow-xl hover:shadow-2xl transition-all hover:scale-110 group"
          aria-label="Open chat"
        >
          <MessageCircle className="h-6 w-6" />
          <span className="absolute -top-1 -right-1 flex h-4 w-4">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-4 w-4 bg-pink-500"></span>
          </span>
          <span className="absolute bottom-full right-0 mb-2 px-3 py-1 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
            Chat with AI
          </span>
        </button>
      )}

      {/* Chat Panel */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 z-40 w-[calc(100vw-3rem)] max-w-md h-[calc(100vh-6rem)] max-h-[700px] bg-white dark:bg-gray-900 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 flex flex-col overflow-hidden animate-in slide-in-from-bottom-4 duration-300">
          {/* Header */}
          <div className="flex items-center justify-between p-4 bg-indigo-500 text-white">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                <Bot className="h-6 w-6" />
              </div>
              <div>
                <h3 className="font-semibold flex items-center gap-2">
                  Store AI
                  <Sparkles className="h-4 w-4" />
                </h3>
                <p className="text-xs text-indigo-100">
                  {isSending ? 'Replying...' : 'Online'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleReset}
                className="text-xs px-2 py-1 bg-white/10 hover:bg-white/20 rounded transition-colors"
                title="New conversation"
              >
                New
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1 hover:bg-white/20 rounded transition-colors"
                aria-label="Close chat"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-950">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] ${
                    msg.role === 'user'
                      ? 'bg-indigo-600 text-white rounded-2xl rounded-br-sm'
                      : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-2xl rounded-bl-sm border border-gray-200 dark:border-gray-700'
                  } px-4 py-3 shadow-sm`}
                >
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>

                  {/* Product cards */}
                  {msg.products && msg.products.length > 0 && (
                    <div className="mt-3 space-y-2">
                      {msg.products.slice(0, 3).map((product: any) => {
                        const pid = product.id || product.product_id;
                        return (
                          <Link
                            key={pid}
                            to={`/product/${pid}`}
                            onClick={() => setIsOpen(false)}
                            className="block bg-gray-50 dark:bg-gray-900 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg p-2 transition-colors border border-gray-200 dark:border-gray-700"
                          >
                            <div className="flex items-center gap-2">
                              <img
                                src={
                                  product.image_url ||
                                  product.image ||
                                  `https://picsum.photos/seed/chat${pid}/60/60`
                                }
                                alt={product.name}
                                className="w-10 h-10 rounded object-cover"
                                referrerPolicy="no-referrer"
                              />
                              <div className="flex-1 min-w-0">
                                <p className="text-xs font-semibold text-gray-900 dark:text-white line-clamp-1">
                                  {product.name}
                                </p>
                                <div className="flex items-center justify-between">
                                  <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400">
                                    ${product.price}
                                  </span>
                                  {product.average_rating && (
                                    <div className="flex items-center">
                                      <Star className="h-3 w-3 text-yellow-400 fill-current" />
                                      <span className="text-xs text-gray-600 dark:text-gray-400 ml-0.5">
                                        {Number(product.average_rating).toFixed(1)}
                                      </span>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                          </Link>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isSending && (
              <div className="flex justify-start">
                <div className="bg-white dark:bg-gray-800 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm border border-gray-200 dark:border-gray-700">
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin text-indigo-600" />
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      Searching...
                    </span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Questions */}
          {messages.length <= 1 && (
            <div className="px-4 py-2.5 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 flex gap-2 overflow-x-auto">
              {[
                'Laptop under $1600',
                'Self-help books',
                'Gaming laptops',
                'Smartphones',
                'Free shipping?',
                'Return policy',
                'Payment methods',
              ].map((q) => (
                <button
                  key={q}
                  onClick={() => handleQuickQuestion(q)}
                  className="text-xs px-3 py-1.5 bg-gray-100 dark:bg-gray-800 hover:bg-indigo-100 dark:hover:bg-indigo-900/30 text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 rounded-full whitespace-nowrap transition-colors border border-gray-200 dark:border-gray-700"
                >
                  {q}
                </button>
              ))}
            </div>
          )}

          {/* Input */}
          <form
            id="chat-form"
            onSubmit={handleSend}
            className="p-3 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 flex items-center gap-2"
          >
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Nhắn tin cho AI..."
              className="flex-1 bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 border border-gray-200 dark:border-gray-700"
              disabled={isSending}
            />
            <button
              type="submit"
              disabled={!input.trim() || isSending}
              className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 dark:disabled:bg-gray-700 text-white p-2 rounded-full transition-colors"
              aria-label="Send"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      )}
    </>
  );
}
