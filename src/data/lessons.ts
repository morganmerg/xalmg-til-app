// Curated starter lessons — each is 5-7 word/phrase pairs drawn from the
// Kalmyk-Russian dictionary. MVP pre-defines them; later they can be
// generated programmatically from dictionary categories.

export type LessonItem = {
  kal: string;
  rus: string;
  // Optional distractor translations for quizzes
  alt?: string[];
};

export type Lesson = {
  id: string;
  emoji: string;
  kal: string;
  rus: string;
  minutes: number;
  order: number;
  items: LessonItem[];
};

export const LESSONS: Lesson[] = [
  {
    id: 'greetings',
    emoji: '👋',
    kal: 'Менд күргх',
    rus: 'Приветствия',
    minutes: 8,
    order: 1,
    items: [
      { kal: 'Мендвт', rus: 'Здравствуйте', alt: ['Радость', 'Хорошо', 'Спасибо'] },
      { kal: 'Сән бәәцхәтн', rus: 'Будьте здоровы', alt: ['Доброе утро', 'До свидания', 'Пожалуйста'] },
      { kal: 'Ханҗанав', rus: 'Спасибо', alt: ['Извините', 'Пожалуйста', 'Здравствуйте'] },
      { kal: 'Сән өдр', rus: 'Добрый день', alt: ['Доброй ночи', 'Доброе утро', 'Привет'] },
      { kal: 'Уульх', rus: 'Плакать', alt: ['Смеяться', 'Петь', 'Говорить'] },
      { kal: 'Баир', rus: 'Радость', alt: ['Грусть', 'Гнев', 'Страх'] },
      { kal: 'Сән', rus: 'Хорошо', alt: ['Плохо', 'Быстро', 'Медленно'] },
    ],
  },
  {
    id: 'family',
    emoji: '👨‍👩‍👧',
    kal: 'Өрк-бүл',
    rus: 'Семья',
    minutes: 10,
    order: 2,
    items: [
      { kal: 'Аав', rus: 'Отец, папа', alt: ['Мать', 'Брат', 'Сестра'] },
      { kal: 'Ээҗ', rus: 'Мать, мама', alt: ['Отец', 'Бабушка', 'Дочь'] },
      { kal: 'Көвүн', rus: 'Сын, мальчик', alt: ['Дочь', 'Брат', 'Друг'] },
      { kal: 'Күүкн', rus: 'Дочь, девочка', alt: ['Сын', 'Сестра', 'Бабушка'] },
      { kal: 'Ах', rus: 'Старший брат', alt: ['Младший брат', 'Отец', 'Дядя'] },
      { kal: 'Эгч', rus: 'Старшая сестра', alt: ['Младшая сестра', 'Мать', 'Тётя'] },
      { kal: 'Өрк', rus: 'Семья, двор', alt: ['Дом', 'Улица', 'Село'] },
    ],
  },
  {
    id: 'steppe',
    emoji: '🐎',
    kal: 'Теегин бәәдл',
    rus: 'Степь и природа',
    minutes: 12,
    order: 3,
    items: [
      { kal: 'Теег', rus: 'Степь', alt: ['Лес', 'Горы', 'Река'] },
      { kal: 'Мөрн', rus: 'Конь, лошадь', alt: ['Корова', 'Верблюд', 'Овца'] },
      { kal: 'Темән', rus: 'Верблюд', alt: ['Конь', 'Баран', 'Волк'] },
      { kal: 'Салькн', rus: 'Ветер', alt: ['Дождь', 'Снег', 'Солнце'] },
      { kal: 'Нарн', rus: 'Солнце', alt: ['Луна', 'Звезда', 'Облако'] },
      { kal: 'Сар', rus: 'Луна, месяц', alt: ['Солнце', 'Год', 'День'] },
      { kal: 'Усн', rus: 'Вода', alt: ['Огонь', 'Земля', 'Воздух'] },
    ],
  },
  {
    id: 'food',
    emoji: '🍵',
    kal: 'Хот-хол',
    rus: 'Еда и чай',
    minutes: 6,
    order: 4,
    items: [
      { kal: 'Цә', rus: 'Чай', alt: ['Молоко', 'Вода', 'Суп'] },
      { kal: 'Өдмг', rus: 'Хлеб', alt: ['Мясо', 'Сыр', 'Масло'] },
      { kal: 'Махн', rus: 'Мясо', alt: ['Рыба', 'Хлеб', 'Фрукты'] },
      { kal: 'Үсн', rus: 'Молоко', alt: ['Вода', 'Чай', 'Кумыс'] },
      { kal: 'Шикр', rus: 'Сахар', alt: ['Соль', 'Мёд', 'Перец'] },
      { kal: 'Давсн', rus: 'Соль', alt: ['Сахар', 'Масло', 'Уксус'] },
    ],
  },
  {
    id: 'numbers',
    emoji: '🔢',
    kal: 'Тооллтын үгмүд',
    rus: 'Числа',
    minutes: 5,
    order: 5,
    items: [
      { kal: 'Негн', rus: 'Один', alt: ['Два', 'Три', 'Четыре'] },
      { kal: 'Хойр', rus: 'Два', alt: ['Один', 'Три', 'Пять'] },
      { kal: 'Һурвн', rus: 'Три', alt: ['Два', 'Четыре', 'Шесть'] },
      { kal: 'Дөрвн', rus: 'Четыре', alt: ['Три', 'Пять', 'Семь'] },
      { kal: 'Тавн', rus: 'Пять', alt: ['Четыре', 'Шесть', 'Восемь'] },
      { kal: 'Зурһан', rus: 'Шесть', alt: ['Пять', 'Семь', 'Девять'] },
      { kal: 'Долан', rus: 'Семь', alt: ['Шесть', 'Восемь', 'Десять'] },
    ],
  },
];

export function getLesson(id: string): Lesson | undefined {
  return LESSONS.find((l) => l.id === id);
}
