import { useState } from 'react';
import { Search, BookOpen, Filter, X } from 'lucide-react';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { ScrollArea } from './ui/scroll-area';
import { Badge } from './ui/badge';
import { scriptures, books, type Scripture } from '../data/scriptures';
import { searchScriptures } from '../../api';
import { useEffect } from 'react';

interface ScriptureLibraryProps {
  onScriptureSelect: (scripture: Scripture) => void;
}

export function ScriptureLibrary({ onScriptureSelect }: ScriptureLibraryProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTestament, setSelectedTestament] = useState<'all' | 'Ветхий Завет' | 'Новый Завет'>('all');
  const [showFilters, setShowFilters] = useState(false);

  const [results, setResults] = useState<Scripture[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
  const timeout = setTimeout(async () => {
    if (!searchQuery.trim()) {
      setResults([]);
      return;
    }

    setIsLoading(true);

    try {
      const data = await searchScriptures(searchQuery);
      setResults(data); // если backend возвращает массив
    } catch (e) {
      console.error(e);
    }

    setIsLoading(false);
  }, 400);

  return () => clearTimeout(timeout);
}, [searchQuery]);

  const groupedByTestament = results.reduce((acc, scripture) => {
    if (!acc[scripture.testament]) {
      acc[scripture.testament] = [];
    }
    acc[scripture.testament].push(scripture);
    return acc;
  }, {} as Record<string, Scripture[]>);

  return (
    <div className="min-h-screen">
      {/* Search Header */}
      <div className="sticky top-[57px] bg-white/95 backdrop-blur-sm border-b border-amber-200 z-40 px-4 py-3 space-y-3 shadow-sm">
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-amber-600" />
            <Input
              type="search"
              placeholder="Поиск по писаниям..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 border-amber-300 focus:border-amber-500"
            />
          </div>
          <Button
            variant="outline"
            size="icon"
            onClick={() => setShowFilters(!showFilters)}
            className={`border-amber-300 ${showFilters ? 'bg-amber-100 text-amber-900' : 'text-amber-700'}`}
          >
            <Filter className="w-4 h-4" />
          </Button>
        </div>

        {showFilters && (
          <div className="flex gap-2 pb-1">
            <Button
              variant={selectedTestament === 'all' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedTestament('all')}
              className={selectedTestament === 'all' 
                ? 'bg-gradient-to-r from-amber-600 to-orange-600 text-white' 
                : 'border-amber-300 text-amber-700'
              }
            >
              Все
            </Button>
            <Button
              variant={selectedTestament === 'Ветхий Завет' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedTestament('Ветхий Завет')}
              className={selectedTestament === 'Ветхий Завет' 
                ? 'bg-gradient-to-r from-amber-600 to-orange-600 text-white' 
                : 'border-amber-300 text-amber-700'
              }
            >
              Ветхий Завет
            </Button>
            <Button
              variant={selectedTestament === 'Новый Завет' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedTestament('Новый Завет')}
              className={selectedTestament === 'Новый Завет' 
                ? 'bg-gradient-to-r from-amber-600 to-orange-600 text-white' 
                : 'border-amber-300 text-amber-700'
              }
            >
              Новый Завет
            </Button>
          </div>
        )}
      </div>

      {/* Results */}
      <div className="px-4 py-4 space-y-4">
        <div className="flex items-center justify-between">
          <p className="text-sm text-amber-700">
            Найдено: {results.length} {results.length === 1 ? 'писание' : 'писаний'}
          </p>
          {(searchQuery || selectedTestament !== 'all') && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setSearchQuery('');
                setSelectedTestament('all');
              }}
              className="text-amber-700 text-xs"
            >
              <X className="w-3 h-3 mr-1" />
              Сбросить
            </Button>
          )}
        </div>

        {Object.entries(groupedByTestament).map(([testament, testamentScriptures]) => (
          <div key={testament} className="space-y-3">

            <div className="space-y-2">
              {testamentScriptures.map((scripture) => (
                <Card
                  key={scripture.id}
                  className="border-amber-200 hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => onScriptureSelect(scripture)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between gap-3 mb-2">
                      <h4 className="font-semibold text-amber-900">
                        {scripture.book} {scripture.chapter}:{scripture.verse}
                      </h4>
                      <Badge variant="outline" className="border-amber-300 text-amber-700 text-xs shrink-0">
                        {scripture.testament === 'Ветхий Завет' ? 'ВЗ' : 'НЗ'}
                      </Badge>
                    </div>
                    <p className="text-sm text-amber-800 leading-relaxed line-clamp-3">
                      {scripture.text}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        ))}

        {results.length === 0 && (
          <Card className="border-amber-200">
            <CardContent className="p-8 text-center space-y-3">
              <div className="bg-amber-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto">
                <Search className="w-8 h-8 text-amber-700" />
              </div>
              <div>
                <h3 className="font-semibold text-amber-900 mb-1">
                  Ничего не найдено
                </h3>
                <p className="text-sm text-amber-700">
                  Попробуйте изменить параметры поиска
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
