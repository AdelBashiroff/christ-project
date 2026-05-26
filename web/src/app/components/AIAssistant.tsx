import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, Loader2, X, BookOpen } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Input } from './ui/input';
import { ScrollArea } from './ui/scroll-area';
import { Badge } from './ui/badge';
import type { Scripture } from '../data/scriptures';
import { askAI } from "../../api";

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface AIAssistantProps {
  selectedScripture: Scripture | null;
  onClearScripture: () => void;
}

export function AIAssistant({ selectedScripture, onClearScripture }: AIAssistantProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (selectedScripture && messages.length === 0) {
      // Automatically provide context when a scripture is selected
      handleAutoExplanation();
    }
  }, [selectedScripture]);

  useEffect(() => {
    // Scroll to bottom when messages change
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleAutoExplanation = async () => {
    if (!selectedScripture) return;

    setIsLoading(true);
    
    // Simulate AI response
    setTimeout(() => {
      const explanation = generateExplanation(selectedScripture);
      setMessages([
        {
          id: Date.now().toString(),
          role: 'assistant',
          content: explanation,
          timestamp: new Date()
        }
      ]);
      setIsLoading(false);
    }, 1000);
  };

  const generateExplanation = (scripture: Scripture): string => {
    // Mock AI explanations based on scripture
    const explanations: Record<number, string> = {
      1: 'Это первый стих Библии, описывающий акт творения. "В начале" указывает на начало времени и материального мира. Бог создал небо (духовную реальность) и землю (материальный мир), демонстрируя Свою абсолютную власть и суверенитет над всем сущим.',
      2: 'Это один из самых известных стихов Библии, который раскрывает суть Евангелия. Он показывает три ключевых истины: 1) Божью любовь к миру, 2) Жертву Христа для спасения, 3) Обещание вечной жизни через веру. Это центральное послание христианства о спасении по благодати через веру.',
      3: 'Псалом 23 - один из самых утешительных текстов Библии. Образ Бога как Пастыря показывает Его заботу, руководство и защиту. "Не буду нуждаться" означает не отсутствие трудностей, а уверенность в том, что Бог обеспечит все необходимое для жизни и духовного роста.',
      4: 'Этот стих из Нагорной проповеди показывает ценность миротворчества в Царстве Божьем. Миротворцы активно стремятся к примирению и гармонии. Они названы "сынами Божиими", потому что отражают характер Бога, Который примирил нас с Собой через Христа.',
      5: 'Притча призывает к полному доверию Богу, а не полагаться только на человеческий разум. Это не отрицание разума, а признание его ограниченности. Когда мы полагаемся на Бога всем сердцем, Он направляет наши пути и дает мудрость, превосходящую наше понимание.',
      6: 'Павел пишет о духовной силе, которую верующие получают через отношения со Христом. Это не о физической способности делать все, а о том, что во Христе мы можем справиться с любыми обстоятельствами - будь то изобилие или нужда, радость или страдание.',
      7: 'Этот стих учит о Божьем провидении в жизни верующих. "Все содействует ко благу" не означает, что все плохое - хорошо, но что Бог может использовать даже трудные обстоятельства для нашего духовного роста и Своих целей.',
      8: 'Исайя обещает обновление силы тем, кто надеется на Господа. Орлы символизируют силу и выносливость. Это обещание духовного обновления, когда человеческие силы истощаются, но Божья сила поддерживает и укрепляет.',
      9: 'Описание истинной любви из знаменитой "Главы о любви". Павел перечисляет характеристики агапе - жертвенной, безусловной любви. Это стандарт христианской любви, которая отражает любовь Бога к нам.',
      10: 'Бог обещает Своему народу надежду и будущее. Этот стих был написан во время вавилонского плена, но применим ко всем верующим. Божьи планы всегда направлены на наше благо, даже когда мы проходим через трудности.',
      11: 'Иисус учит о приоритетах в жизни. Искать Царство Божье означает ставить Бога на первое место в наших сердцах и жизни. Когда мы это делаем, Он заботится о наших материальных нуждах.',
      12: 'Псалом утверждает, что Бог - наше убежище в трудные времена. Он не только защита, но и источник силы. "Скорый помощник" означает, что Он всегда готов прийти на помощь в нужный момент.',
      13: 'Ключевой стих о спасении по благодати через веру. Спасение - не результат наших дел, а дар Божий. Это освобождает от попыток заработать спасение и дает уверенность в вечной жизни.',
      14: 'Мудрый совет о воспитании детей. Наставление в юности формирует характер и ценности на всю жизнь. Это призыв родителям быть примером и учить детей Божьим путям с раннего возраста.',
      15: 'Иисус провозглашает Свою исключительность. Он не просто указывает путь - Он и есть путь к Отцу. Истина и жизнь также воплощены в Нем. Это центральное утверждение христианской веры.',
      16: 'Слово Божье освещает наш жизненный путь, помогая избежать греха и принимать правильные решения. Оно руководит нашими шагами и дает мудрость для каждодневной жизни.',
      17: 'Павел описывает "плод Духа" - результат жизни под водительством Святого Духа. Эти качества развиваются не человеческими усилиями, а действием Духа в сердце верующего.',
      18: 'Одна из Десяти Заповедей. Почитание родителей - основа здорового общества. Это включает уважение, заботу и послушание. Обещание долголетия связано с благословением послушания Божьим заповедям.',
      19: 'Писание богодухновенно - вдохновлено Богом. Это утверждение о божественном происхождении и авторитете Библии. Она полезна для обучения, исправления и духовного роста верующих.',
      20: 'Известный стих о времени и сезонах жизни. Все в жизни имеет свое время в Божьем плане. Это учит терпению, принятию перемен и доверию Божьему совершенному времени.'
    };

    return explanations[scripture.id] || `Это писание из книги ${scripture.book} содержит важное духовное наставление. Текст "${scripture.text}" призывает к размышлению о Божьей мудрости и Его воле для нашей жизни. Контекст этого отрывка связан с общими темами ${scripture.testament === 'Ветхий Завет' ? 'Ветхого Завета' : 'Нового Завета'}, которые раскрывают Божий характер и Его отношения с человечеством.`;
  };

  const handleSend = async () => {
  if (!input.trim() || isLoading) return;

  const userMessage: Message = {
    id: Date.now().toString(),
    role: 'user',
    content: input,
    timestamp: new Date()
  };

  setMessages(prev => [...prev, userMessage]);
  setInput('');
  setIsLoading(true);

  try {
    const res = await askAI(input);

    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: res.answer || 'Нет ответа от сервера',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, assistantMessage]);
  } catch (e) {
    setMessages(prev => [...prev, {
      id: (Date.now() + 2).toString(),
      role: 'assistant',
      content: 'Ошибка подключения к AI сервису',
      timestamp: new Date()
    }]);
  }

  setIsLoading(false);
};

  const generateAIResponse = (question: string, scripture: Scripture | null): string => {
    const lowerQuestion = question.toLowerCase();
    
    if (lowerQuestion.includes('применить') || lowerQuestion.includes('применение')) {
      return 'Применение этого писания в повседневной жизни начинается с молитвы и размышления. Попросите Бога показать, как эти слова относятся к вашей текущей ситуации. Ведите духовный дневник, записывая свои мысли и откровения. Делитесь этими истинами с другими верующими и ищите возможности жить в соответствии с этим учением.';
    }
    
    if (lowerQuestion.includes('почему') || lowerQuestion.includes('зачем')) {
      return 'Каждое писание имеет глубокую цель в общем плане Божьего откровения. Это учение призвано формировать наш характер, укреплять веру и направлять в принятии решений. Бог использует Свое Слово, чтобы говорить с нами, исправлять и вести нас по правильному пути.';
    }
    
    if (lowerQuestion.includes('контекст') || lowerQuestion.includes('история')) {
      return scripture 
        ? `Книга ${scripture.book} была написана в определенном историческом и культурном контексте. Понимание обстоятельств написания помогает глубже понять смысл. ${scripture.testament} содержит различные литературные жанры - историю, поэзию, пророчества и послания, каждый со своими особенностями толкования.`
        : 'Исторический контекст писания важен для правильного понимания. Рекомендую изучить время написания, аудиторию и цель автора для более глубокого понимания текста.';
    }
    
    if (lowerQuestion.includes('молитва') || lowerQuestion.includes('молиться')) {
      return 'Основываясь на этом писании, вы можете молиться: "Господи, открой мое сердце для понимания Твоего Слова. Помоги мне не только читать, но и применять эти истины в моей жизни. Дай мне мудрость и силу Духа Святого жить в соответствии с этим учением. Аминь."';
    }

    return 'Спасибо за ваш вопрос! Это глубокая тема для размышления. Я рекомендую также изучить связанные отрывки Писания и прочитать комментарии признанных богословов. Помните, что Святой Дух - наш главный Учитель в понимании Божьего Слова. Молитесь об откровении и будьте открыты к тому, что Бог хочет сказать вам через этот текст.';
  };

  return (
    <div className="flex flex-col h-[calc(100vh-137px)]">
      {/* Context Card */}
      {selectedScripture && (
        <div className="px-4 pt-4">
          <Card className="border-amber-300 bg-amber-50">
            <CardContent className="p-3">
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-start gap-2 flex-1 min-w-0">
                  <BookOpen className="w-4 h-4 text-amber-700 mt-0.5 shrink-0" />
                  <div className="min-w-0">
                    <p className="text-xs font-semibold text-amber-900">
                      {selectedScripture.book} {selectedScripture.chapter}:{selectedScripture.verse}
                    </p>
                    <p className="text-xs text-amber-700 line-clamp-2 mt-1">
                      {selectedScripture.text}
                    </p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6 shrink-0"
                  onClick={onClearScripture}
                >
                  <X className="w-3 h-3 text-amber-700" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Messages Area */}
      <ScrollArea className="flex-1 px-4 py-4" ref={scrollRef}>
        <div className="space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-12 space-y-4">
              <div className="bg-gradient-to-br from-amber-100 to-orange-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto">
                <Bot className="w-10 h-10 text-amber-700" />
              </div>
              <div className="space-y-2">
                <h3 className="text-lg font-semibold text-amber-900">
                  AI-помощник готов помочь
                </h3>
                <p className="text-sm text-amber-700 max-w-sm mx-auto">
                  Задайте вопрос о писании, попросите разъяснить контекст или узнайте, как применить это учение в жизни
                </p>
              </div>
              <div className="flex flex-wrap gap-2 justify-center max-w-md mx-auto">
                <Badge 
                  variant="secondary" 
                  className="bg-amber-100 text-amber-800 cursor-pointer hover:bg-amber-200"
                  onClick={() => setInput('Как применить это в жизни?')}
                >
                  Как применить?
                </Badge>
                <Badge 
                  variant="secondary" 
                  className="bg-amber-100 text-amber-800 cursor-pointer hover:bg-amber-200"
                  onClick={() => setInput('Расскажи о контексте')}
                >
                  Контекст
                </Badge>
                <Badge 
                  variant="secondary" 
                  className="bg-amber-100 text-amber-800 cursor-pointer hover:bg-amber-200"
                  onClick={() => setInput('Предложи молитву')}
                >
                  Молитва
                </Badge>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {message.role === 'assistant' && (
                <div className="bg-gradient-to-br from-amber-600 to-orange-600 w-8 h-8 rounded-full flex items-center justify-center shrink-0">
                  <Bot className="w-5 h-5 text-white" />
                </div>
              )}
              
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-gradient-to-br from-amber-600 to-orange-600 text-white'
                    : 'bg-white border border-amber-200 text-amber-950'
                }`}
              >
                <p className="text-sm leading-relaxed whitespace-pre-wrap">
                  {message.content}
                </p>
              </div>

              {message.role === 'user' && (
                <div className="bg-amber-700 w-8 h-8 rounded-full flex items-center justify-center shrink-0">
                  <User className="w-5 h-5 text-white" />
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3 justify-start">
              <div className="bg-gradient-to-br from-amber-600 to-orange-600 w-8 h-8 rounded-full flex items-center justify-center shrink-0">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div className="bg-white border border-amber-200 rounded-2xl px-4 py-3">
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin text-amber-700" />
                  <span className="text-sm text-amber-700">Думаю...</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="p-4 bg-white border-t border-amber-200">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Задайте вопрос о писании..."
            className="flex-1 border-amber-300 focus:border-amber-500"
            disabled={isLoading}
          />
          <Button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700 text-white shrink-0"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
