import { Book, Sparkles, MessageCircle, Home } from 'lucide-react';
import { useState } from 'react';
import { Button } from './components/ui/button';
import { Card, CardContent } from './components/ui/card';
import { scriptures, type Scripture } from './data/scriptures';
import { RandomScripture } from './components/RandomScripture';
import { ScriptureLibrary } from './components/ScriptureLibrary';
import { AIAssistant } from './components/AIAssistant';
import { getRandomScripture } from "./api";

type View = 'home' | 'library' | 'ai';

export default function App() {
  const [currentView, setCurrentView] = useState<View>('home');
  const [selectedScripture, setSelectedScripture] = useState<Scripture | null>(null);

  const handleScriptureSelect = (scripture: Scripture) => {
    setSelectedScripture(scripture);
    setCurrentView('ai');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-white to-orange-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-amber-200 sticky top-0 z-50 shadow-sm">
        <div className="px-4 py-3">
          <div className="flex items-center justify-center gap-2">
            <div className="bg-gradient-to-br from-amber-600 to-orange-600 p-2 rounded-xl shadow-lg">
              <Book className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="font-semibold text-lg text-amber-900">
                Справочник Священника
              </h1>
              <p className="text-xs text-amber-700">Карманный гид по писаниям</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="pb-20">
        {currentView === 'home' && (
          <div className="px-4 py-6 space-y-6">
            {/* Hero Section */}
            <Card className="bg-gradient-to-br from-amber-600 to-orange-600 border-0 shadow-xl">
              <CardContent className="p-6 text-white text-center space-y-3">
                <Sparkles className="w-12 h-12 mx-auto mb-2" />
                <h2 className="text-xl font-semibold">Получите мудрое наставление</h2>
                <p className="text-amber-100 text-sm">
                  Случайное писание одним кликом
                </p>
              </CardContent>
            </Card>

            {/* Random Scripture Component */}
            <RandomScripture onScriptureSelect={handleScriptureSelect} />

            {/* Features */}
            <div className="space-y-3">
              <h3 className="text-sm font-semibold text-amber-900 px-2">
                Возможности приложения
              </h3>
              <div className="grid gap-3">
                <Card 
                  className="hover:shadow-lg transition-shadow cursor-pointer border-amber-200"
                  onClick={() => setCurrentView('library')}
                >
                  <CardContent className="p-4 flex items-start gap-3">
                    <div className="bg-amber-100 p-2 rounded-lg">
                      <Book className="w-5 h-5 text-amber-700" />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold text-amber-900 mb-1">
                        Справочник писаний
                      </h4>
                      <p className="text-sm text-amber-700">
                        Полная библиотека христианских текстов
                      </p>
                    </div>
                  </CardContent>
                </Card>

                <Card 
                  className="hover:shadow-lg transition-shadow cursor-pointer border-amber-200"
                  onClick={() => setCurrentView('ai')}
                >
                  <CardContent className="p-4 flex items-start gap-3">
                    <div className="bg-orange-100 p-2 rounded-lg">
                      <MessageCircle className="w-5 h-5 text-orange-700" />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold text-amber-900 mb-1">
                        AI-помощник
                      </h4>
                      <p className="text-sm text-amber-700">
                        Разъяснение контекста и смысла
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        )}

        {currentView === 'library' && (
          <ScriptureLibrary onScriptureSelect={handleScriptureSelect} />
        )}

        {currentView === 'ai' && (
          <AIAssistant 
            selectedScripture={selectedScripture}
            onClearScripture={() => setSelectedScripture(null)}
          />
        )}
      </main>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-amber-200 shadow-lg">
        <div className="grid grid-cols-3 gap-1 px-2 py-2">
          <Button
            variant={currentView === 'home' ? 'default' : 'ghost'}
            className={`flex flex-col items-center gap-1 h-auto py-2 ${
              currentView === 'home' 
                ? 'bg-gradient-to-br from-amber-600 to-orange-600 text-white' 
                : 'text-amber-700'
            }`}
            onClick={() => setCurrentView('home')}
          >
            <Home className="w-5 h-5" />
            <span className="text-xs">Главная</span>
          </Button>

          <Button
            variant={currentView === 'library' ? 'default' : 'ghost'}
            className={`flex flex-col items-center gap-1 h-auto py-2 ${
              currentView === 'library' 
                ? 'bg-gradient-to-br from-amber-600 to-orange-600 text-white' 
                : 'text-amber-700'
            }`}
            onClick={() => setCurrentView('library')}
          >
            <Book className="w-5 h-5" />
            <span className="text-xs">Справочник</span>
          </Button>

          <Button
            variant={currentView === 'ai' ? 'default' : 'ghost'}
            className={`flex flex-col items-center gap-1 h-auto py-2 ${
              currentView === 'ai' 
                ? 'bg-gradient-to-br from-amber-600 to-orange-600 text-white' 
                : 'text-amber-700'
            }`}
            onClick={() => setCurrentView('ai')}
          >
            <MessageCircle className="w-5 h-5" />
            <span className="text-xs">AI-помощник</span>
          </Button>
        </div>
      </nav>
    </div>
  );
}
