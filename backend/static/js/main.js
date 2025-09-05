// Este código se ejecutará una vez que todo el contenido de la página se haya cargado.
document.addEventListener('DOMContentLoaded', (event) => {
    
    // 1. Buscamos todos los elementos que tengan la clase 'alert'.
    //    querySelectorAll devuelve una lista de todos los mensajes flash que se estén mostrando.
    const flashMessages = document.querySelectorAll('.alert');
    
    // 2. Si se encontraron mensajes...
    if (flashMessages) {
        
        // 3. Recorremos cada uno de los mensajes encontrados.
        flashMessages.forEach(function(message) {
            
            // 4. Usamos setTimeout para ejecutar una acción después de un tiempo.
            //    5000 milisegundos = 5 segundos.
            setTimeout(function() {
                // 5. Añadimos una clase 'fade-out' al mensaje.
                //    Esto activará nuestra animación de CSS.
                message.classList.add('fade-out');
            }, 3000); // El mensaje empezará a desvanecerse después de 5 segundos.

            // 6. Opcional: Después de que la animación termine, eliminamos el elemento por completo.
            //    La animación dura 0.5 segundos (500ms).
            setTimeout(function() {
                message.remove(); // Esto limpia el HTML.
            }, 3500); // 5000ms de espera + 500ms de animación.
        });
    }
});