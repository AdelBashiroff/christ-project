import { useState } from 'react';
import { Sparkles, RefreshCw, Share2, Bookmark } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { scriptures, type Scripture } from '../data/scriptures';
import { toast } from 'sonner';
import { getRandomScripture } from "../../api";

interface RandomScriptureProps {
  onScriptureSelect: (scripture: Scripture) => void;
}

export function RandomScripture({ onScriptureSelect }: RandomScriptureProps) {
  const [currentScripture, setCurrentScripture] = useState<Scripture | null>(null);
  const [isAnimating, setIsAnimating] = useState(false);
  const [savedScriptures, setSavedScriptures] = useState<Set<number>>(new Set());

  const generateRandomScripture = async () => {
    setIsAnimating(true);

    setTimeout(async () => {
      const data = await getRandomScripture();
      setCurrentScripture(data);
      setIsAnimating(false);
    }, 300);
  };

  const handleSave = () => {
    if (currentScripture) {
      setSavedScriptures(prev => {
        const newSet = new Set(prev);
        if (newSet.has(currentScripture.id)) {
          newSet.delete(currentScripture.id);
          toast.success('Убрано из избранного');
        } else {
          newSet.add(currentScripture.id);
          toast.success('Добавлено в избранное');
        }
        return newSet;
      });
    }
  };

  const handleShare = async () => {
    if (currentScripture) {
      const text = `${currentScripture.book} ${currentScripture.chapter}:${currentScripture.verse}\n\n"${currentScripture.text}"`;
      
      if (navigator.share) {
        try {
          await navigator.share({ text });
          toast.success('Писание отправлено');
        } catch (err) {
          // User cancelled or error
        }
      } else {
        navigator.clipboard.writeText(text);
        toast.success('Скопировано в буфер обмена');
      }
    }
  };

  return (
    <div className="space-y-4">
      {!currentScripture ? (
        <Card className="border-amber-200 shadow-lg">
          <CardContent className="p-8 text-center space-y-4">
            <div className="bg-gradient-to-br from-amber-100 to-orange-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto">
              <Sparkles className="w-10 h-10 text-amber-700" />
            </div>
            <div className="space-y-2">
              <h3 className="text-lg font-semibold text-amber-900">
                Случайное писание
              </h3>
              <p className="text-sm text-amber-700">
                Получите мудрое наставление на сегодня
              </p>
            </div>
            <Button
              onClick={generateRandomScripture}
              className="bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700 text-white px-8 py-6 text-base rounded-xl shadow-lg"
            >
              <Sparkles className="w-5 h-5 mr-2" />
              Получить писание
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Card className={`border-amber-200 shadow-xl transition-all duration-300 ${
          isAnimating ? 'opacity-0 scale-95' : 'opacity-100 scale-100'
        }`}>
          <CardContent className="p-0">
            {/* Testament Badge */}
            <div className="bg-gradient-to-r from-amber-600 to-orange-600 px-4 py-2 text-center">
              <span className="text-xs text-white font-medium">
                {currentScripture.testament}
              </span>
            </div>

            {/* Scripture Content */}
            <div className="p-6 space-y-4">
              <div className="text-center space-y-2">
                <h3 className="text-lg font-semibold text-amber-900">
                  {currentScripture.book} {currentScripture.chapter}:{currentScripture.verse}
                </h3>
              </div>

              <div className="bg-amber-50 p-4 rounded-xl border border-amber-200">
                <p className="text-amber-950 leading-relaxed text-center italic">
                  "{currentScripture.text}"
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={generateRandomScripture}
                  className="flex-1 border-amber-300 text-amber-700 hover:bg-amber-50"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Новое
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleSave}
                  className={`border-amber-300 hover:bg-amber-50 ${
                    savedScriptures.has(currentScripture.id)
                      ? 'bg-amber-100 text-amber-900'
                      : 'text-amber-700'
                  }`}
                >
                  <Bookmark className={`w-4 h-4 ${
                    savedScriptures.has(currentScripture.id) ? 'fill-current' : ''
                  }`} />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleShare}
                  className="border-amber-300 text-amber-700 hover:bg-amber-50"
                >
                  <Share2 className="w-4 h-4" />
                </Button>
              </div>

              <Button
                onClick={() => onScriptureSelect(currentScripture)}
                className="w-full bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-700 hover:to-amber-700 text-white"
              >
                <MessageCircle className="w-4 h-4 mr-2" />
                Узнать больше с AI
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// Import MessageCircle from lucide-react
import { MessageCircle } from 'lucide-react';
