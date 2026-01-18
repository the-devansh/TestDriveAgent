import VoiceInterface from "@/components/VoiceInterface";

export default function Home() {
  return (
    <main className="min-h-screen bg-neutral-950 flex flex-col items-center justify-center p-4">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[25%] -left-[25%] w-[50%] h-[50%] bg-blue-500/20 rounded-full blur-[120px]" />
        <div className="absolute -bottom-[25%] -right-[25%] w-[50%] h-[50%] bg-purple-500/20 rounded-full blur-[120px]" />
      </div>

      <div className="z-10 w-full max-w-4xl space-y-12 text-center">
        <div className="space-y-4">
          <h1 className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-white to-purple-400 tracking-tight">
            Next-Gen Test Drive
          </h1>
          <p className="text-gray-400 text-lg max-w-xl mx-auto">
            Book your dream ride using our AI-powered voice assistant.
            Seamless integration, instant confirmation.
          </p>
        </div>

        <VoiceInterface />
      </div>

      <footer className="mt-20 text-gray-600 text-sm">
        Built with LangGraph & Hugging Face
      </footer>
    </main>
  );
}
