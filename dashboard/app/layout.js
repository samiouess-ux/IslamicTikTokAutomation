import "./globals.css";

export const metadata = {
  title: "Quran Studio | لوحة المتابعة",
  description: "لوحة خاصة لمتابعة محرك فيديوهات القرآن الكريم"
};

export default function RootLayout({ children }) {
  return (
    <html lang="ar" dir="rtl">
      <body>{children}</body>
    </html>
  );
}
