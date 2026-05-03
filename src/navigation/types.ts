export type RootStackParamList = {
  Home: undefined;
  Tabs: undefined;
  Lesson: { lessonId: string };
  Dictionary: undefined;
  EntryDetail: { id: number };
  EntryByLemma: { lemma: string };
  Profile: undefined;
};
