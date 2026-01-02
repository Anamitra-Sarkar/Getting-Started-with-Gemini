import './globals.css'
import { FirebaseProvider } from '../lib/firebase'
import { ToastProvider } from '../components/Toast'

export const metadata = {
  title: 'Vaelis',
  description: 'Vaelis AI — General Intelligence Platform',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <FirebaseProvider>
          <ToastProvider>
            {children}
          </ToastProvider>
        </FirebaseProvider>
      </body>
    </html>
  )
}
