import React, { useEffect } from 'react';
import { AlertTriangle, CheckCircle, Info, Clock, X } from 'lucide-react';

const AlertToast = ({ type = 'info', message, duration = 5000, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const getStyles = () => {
    switch (type) {
      case 'success':
        return {
          bg: 'bg-green-50',
          border: 'border-green-200',
          icon: <CheckCircle className="w-5 h-5 text-green-600" />,
          textColor: 'text-green-800'
        };
      case 'error':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          icon: <AlertTriangle className="w-5 h-5 text-red-600" />,
          textColor: 'text-red-800'
        };
      case 'warning':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          icon: <AlertTriangle className="w-5 h-5 text-yellow-600" />,
          textColor: 'text-yellow-800'
        };
      default:
        return {
          bg: 'bg-blue-50',
          border: 'border-blue-200',
          icon: <Info className="w-5 h-5 text-blue-600" />,
          textColor: 'text-blue-800'
        };
    }
  };

  const styles = getStyles();

  return (
    <div className={`fixed bottom-4 right-4 max-w-md rounded-lg border-l-4 p-4 shadow-lg ${styles.bg} ${styles.border} animate-slide-in-up`}>
      <div className="flex items-start gap-3">
        {styles.icon}
        <div className="flex-1">
          <p className={`font-semibold ${styles.textColor}`}>{message}</p>
        </div>
        <button
          onClick={onClose}
          className="flex-shrink-0 text-gray-400 hover:text-gray-600"
        >
          <X className="w-5 h-5" />
        </button>
      </div>
      {/* Progress bar */}
      <div className="mt-2 h-1 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${
            type === 'success' ? 'bg-green-600' :
            type === 'error' ? 'bg-red-600' :
            type === 'warning' ? 'bg-yellow-600' :
            'bg-blue-600'
          } animate-shrink`}
          style={{
            animation: `shrink ${duration}ms linear forwards`
          }}
        />
      </div>

      <style>{`
        @keyframes slide-in-up {
          from {
            transform: translateY(400px);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }
        
        @keyframes shrink {
          from {
            width: 100%;
          }
          to {
            width: 0%;
          }
        }
        
        .animate-slide-in-up {
          animation: slide-in-up 0.3s ease-out;
        }
        
        .animate-shrink {
          animation: shrink ${duration}ms linear forwards;
        }
      `}</style>
    </div>
  );
};

export default AlertToast;
