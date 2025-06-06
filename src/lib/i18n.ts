import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Translations organized by feature
const resources = {
  en: {
    translation: {
      // App & Navigation
      'app.title': 'Testimony Vault',
      'nav.dashboard': 'Dashboard',
      'nav.upload': 'Upload',
      'nav.search': 'Search',
      'nav.about': 'About',
      'nav.uploadFiles': 'Upload Files',
      'footer.copyright': 'Testimony Vault ©',

      // Dashboard
      'dashboard.title': 'Testimony Dashboard',
      'dashboard.subtitle': 'Manage and explore church testimonies',
      'dashboard.noTestimonies': 'No testimonies found',
      'dashboard.noTestimoniesSubtitle': 'Start by uploading your first testimony.',
      'dashboard.adjustFilters': 'Try adjusting your search or filters to find what you\'re looking for.',
      'dashboard.connectionError': 'Connection Error',
      'dashboard.retry': 'Retry',

      // Upload
      'upload.title': 'Upload Testimonies',
      'upload.subtitle': 'Upload MP3 recordings of testimonies to transcribe',
      'upload.instructions': 'Instructions',
      'upload.instruction1': 'Files must be in MP3 format',
      'upload.instruction2': 'Maximum file size: 10 MB per file',
      'upload.instruction3': 'You can upload multiple files at once',
      'upload.instruction4': 'Recommended recording length: 2-5 minutes per file',
      'upload.instruction5': 'Fill in all required metadata for better organization',
      'upload.instruction6': 'Recorded dates are automatically detected from file modification dates',
      'upload.instruction7': 'You can manually override any recorded date if needed',
      'upload.instruction8': 'Setting a date for one file will auto-fill all files without dates',
      'upload.instruction9': 'Each file will be sent as a separate request for processing',
      'upload.instruction10': 'Transcription will begin automatically after upload',
      'upload.instruction11': 'You can continue uploading more testimonies after the current batch',

      // File Upload
      'fileUpload.dropzone': 'Drag & drop your MP3 files here or click to select',
      'fileUpload.churchLocation': 'Church Location',
      'fileUpload.selectChurch': 'Select a church',
      'fileUpload.recordedDate': 'Recorded Date',
      'fileUpload.tags': 'Tags',
      'fileUpload.tagsPlaceholder': 'Add tag...',
      'fileUpload.addTag': 'Add Tag',
      'fileUpload.uploadFiles': 'Upload Files',
      'fileUpload.uploading': 'Uploading...',
      'fileUpload.remove': 'Remove',

      // Search & Filters
      'search.placeholder': 'Search testimonies...',
      'filters.status': 'Status',
      'filters.church': 'Church',
      'filters.tags': 'Tags',
      'filters.all': 'All',
      'filters.pending': 'Pending',
      'filters.completed': 'Completed',
      'filters.failed': 'Failed',

      // Pagination
      'pagination.showing': 'Showing',
      'pagination.of': 'of',
      'pagination.results': 'results',
      'pagination.previous': 'Previous',
      'pagination.next': 'Next',

      // General UI
      'button.viewDetails': 'View Details',
      'button.close': 'Close',
      'button.cancel': 'Cancel',
      'button.save': 'Save',
      'loading': 'Loading...',

      // Status
      'status.processing': 'Processing',
      'status.completed': 'Completed',
      'status.failed': 'Failed',

      // Toasts & Messages
      'toast.uploadSuccess': 'Testimony uploaded successfully!',
      'toast.uploadError': 'Failed to upload testimony',
      'toast.fileTooLarge': 'File size must be less than 10 MB',
      'toast.invalidFileType': 'Please upload MP3 files only',
      'toast.selectFiles': 'Please select at least one audio file',
      'toast.selectChurchLocation': 'Please select a church location',

      // Form Validation
      'form.selectChurch': 'Please select a church location',
      'form.minOneFile': 'At least one audio file is required',
      'form.fileSizeLimit': 'All files must be less than 10 MB',

      // Additional UI
      'files.selected': 'file(s) selected',
      'files.totalSize': 'Total size',
      'files.tip': '💡 Tip: Dates are auto-detected from file modification time. You can manually override any date, and setting a date for one file will apply it to all files without dates',

      // Search Page
      'searchPage.title': 'Search Testimonies',
      'searchPage.subtitle': 'Search through transcribed testimonies using keywords or phrases',
      'searchPage.placeholder': 'Search by keywords, church location, or content...',
      'searchPage.noResults': 'No results found',
      'searchPage.noResultsSubtitle': 'Try different keywords or check your spelling',
      'searchPage.startSearching': 'Start searching',
      'searchPage.startSearchingSubtitle': 'Enter keywords or phrases to search through testimony transcripts',

      // Filters
      'filters.title': 'Filters',
      'filters.reset': 'Reset',
      'filters.selectStatus': 'Select status',
      'filters.allStatuses': 'All Statuses',
      'filters.processing': 'Processing',
      'filters.selectChurchLocation': 'Select church location',
      'filters.allLocations': 'All Locations',
      'filters.addTag': 'Add tag and press Enter',

      // Testimony Card
      'testimonyCard.recorded': 'Recorded',
      'testimonyCard.transcriptionComplete': 'Transcription complete',
      'testimonyCard.transcribing': 'Transcribing...',
      'testimonyCard.transcriptionFailed': 'Transcription failed',
      'testimonyCard.awaitingTranscription': 'Awaiting transcription',
      'testimonyCard.unknownFile': 'Unknown File',
      'testimonyCard.unknownChurch': 'Unknown Church',
    }
  },
  es: {
    translation: {
      // App & Navigation
      'app.title': 'Testimony Vault',
      'nav.dashboard': 'Panel de Control',
      'nav.upload': 'Subir',
      'nav.search': 'Buscar',
      'nav.about': 'Acerca de',
      'nav.uploadFiles': 'Subir Archivos',
      'footer.copyright': 'Testimony Vault ©',

      // Dashboard
      'dashboard.title': 'Testimonios',
      'dashboard.subtitle': 'Gestionar y explorar testimonios de la iglesia',
      'dashboard.noTestimonies': 'No se encontraron testimonios',
      'dashboard.noTestimoniesSubtitle': 'Comienza subiendo tu primer testimonio.',
      'dashboard.adjustFilters': 'Intenta ajustar tu búsqueda o filtros para encontrar lo que buscas.',
      'dashboard.connectionError': 'Error de Conexión',
      'dashboard.retry': 'Reintentar',

      // Upload
      'upload.title': 'Subir Testimonios',
      'upload.subtitle': 'Sube grabaciones MP3 de testimonios para transcribir',
      'upload.instructions': 'Instrucciones',
      'upload.instruction1': 'Los archivos deben estar en formato MP3',
      'upload.instruction2': 'Tamaño máximo de archivo: 10 MB por archivo',
      'upload.instruction3': 'Puedes subir múltiples archivos a la vez',
      'upload.instruction4': 'Duración recomendada de grabación: 2-5 minutos por archivo',
      'upload.instruction5': 'Completa todos los metadatos requeridos para mejor organización',
      'upload.instruction6': 'Las fechas de grabación se detectan automáticamente desde las fechas de modificación del archivo',
      'upload.instruction7': 'Puedes anular manualmente cualquier fecha grabada si es necesario',
      'upload.instruction8': 'Establecer una fecha para un archivo completará automáticamente todos los archivos sin fechas',
      'upload.instruction9': 'Cada archivo será enviado como una solicitud separada para procesamiento',
      'upload.instruction10': 'La transcripción comenzará automáticamente después de la subida',
      'upload.instruction11': 'Puedes continuar subiendo más testimonios después del lote actual',

      // File Upload
      'fileUpload.dropzone': 'Arrastra archivos MP3 aquí o haz clic para seleccionar',
      'fileUpload.churchLocation': 'Ubicación de la Iglesia',
      'fileUpload.selectChurch': 'Selecciona una iglesia',
      'fileUpload.recordedDate': 'Fecha de Grabación',
      'fileUpload.tags': 'Etiquetas',
      'fileUpload.tagsPlaceholder': 'Añadir etiqueta...',
      'fileUpload.addTag': 'Añadir Etiqueta',
      'fileUpload.uploadFiles': 'Subir Archivos',
      'fileUpload.uploading': 'Subiendo...',
      'fileUpload.remove': 'Eliminar',

      // Search & Filters
      'search.placeholder': 'Buscar testimonios...',
      'filters.status': 'Estado',
      'filters.church': 'Iglesia',
      'filters.tags': 'Etiquetas',
      'filters.all': 'Todos',
      'filters.pending': 'Pendiente',
      'filters.completed': 'Completado',
      'filters.failed': 'Fallido',

      // Pagination
      'pagination.showing': 'Mostrando',
      'pagination.of': 'de',
      'pagination.results': 'resultados',
      'pagination.previous': 'Anterior',
      'pagination.next': 'Siguiente',

      // General UI
      'button.viewDetails': 'Ver Detalles',
      'button.close': 'Cerrar',
      'button.cancel': 'Cancelar',
      'button.save': 'Guardar',
      'loading': 'Cargando...',

      // Status
      'status.processing': 'Procesando',
      'status.completed': 'Completado',
      'status.failed': 'Fallido',

      // Toasts & Messages
      'toast.uploadSuccess': '¡Testimonio subido exitosamente!',
      'toast.uploadError': 'Error al subir testimonio',
      'toast.fileTooLarge': 'El tamaño del archivo debe ser menor a 10 MB',
      'toast.invalidFileType': 'Por favor sube solo archivos MP3',
      'toast.selectFiles': 'Por favor selecciona al menos un archivo de audio',
      'toast.selectChurchLocation': 'Por favor selecciona una ubicación de iglesia',

      // Form Validation
      'form.selectChurch': 'Por favor selecciona una ubicación de iglesia',
      'form.minOneFile': 'Se requiere al menos un archivo de audio',
      'form.fileSizeLimit': 'Todos los archivos deben ser menores a 10 MB',

      // Additional UI
      'files.selected': 'archivo(s) seleccionado(s)',
      'files.totalSize': 'Tamaño total',
      'files.tip': '💡 Consejo: Las fechas se detectan automáticamente del tiempo de modificación del archivo. Puedes anular manualmente cualquier fecha, y establecer una fecha para un archivo la aplicará a todos los archivos sin fechas',

      // Search Page
      'searchPage.title': 'Buscar Testimonios',
      'searchPage.subtitle': 'Busca a través de testimonios transcritos usando palabras clave o frases',
      'searchPage.placeholder': 'Buscar por palabras clave, ubicación de iglesia, o contenido...',
      'searchPage.noResults': 'No se encontraron resultados',
      'searchPage.noResultsSubtitle': 'Intenta con diferentes palabras clave o verifica la ortografía',
      'searchPage.startSearching': 'Comenzar búsqueda',
      'searchPage.startSearchingSubtitle': 'Ingresa palabras clave o frases para buscar a través de las transcripciones de testimonios',

      // Filters
      'filters.title': 'Filtros',
      'filters.reset': 'Restablecer',
      'filters.selectStatus': 'Seleccionar estado',
      'filters.allStatuses': 'Todos los Estados',
      'filters.processing': 'Procesando',
      'filters.selectChurchLocation': 'Seleccionar ubicación de iglesia',
      'filters.allLocations': 'Todas las Ubicaciones',
      'filters.addTag': 'Añadir etiqueta y presiona Enter',

      // Testimony Card
      'testimonyCard.recorded': 'Grabado',
      'testimonyCard.transcriptionComplete': 'Transcripción completada',
      'testimonyCard.transcribing': 'Transcribiendo...',
      'testimonyCard.transcriptionFailed': 'Transcripción fallida',
      'testimonyCard.awaitingTranscription': 'Esperando transcripción',
      'testimonyCard.unknownFile': 'Archivo Desconocido',
      'testimonyCard.unknownChurch': 'Iglesia Desconocida',
    }
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'es',
    lng: 'es', // Default to Spanish

    interpolation: {
      escapeValue: false // React already escapes values
    },

    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage']
    }
  });

export default i18n;
