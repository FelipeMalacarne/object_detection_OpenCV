# object_detection_OpenCV
Using OpenCV Library to track ingame objects

-  Projeto iniciado a partir da ideia de detectar e reconhecer objetos em imagens usando a library OpenCV. 

- Aplicação captura a tela da janela de escolha tirando várias screenshots por segundo.
    - A fim de melhorar a performance desse passo, foi feito a substituição do uso das funções de screenshot das libraries pyautogui e Pillow para a utilização direta da API do windows. Isso trouxe um aumento na taxa de quadros de 20fps para 70fps na captura da tela sem processamento.

- É feito o processamento de cada frame capturado utilizando a library OpenCV, destacando os objetos detectados no output de video em tempo real

- Função de pre-processamento de imagens, manipulação e aplicação em tempo real de um filtro de Saturation, Hue e Value (HSV) que pode ser utilizado para apagar os pixels fora do range estipulado pelo filtro, simplificando a imagen a fim de atuar como estágio de pre-processamento da imagem.

- Aplicação de conceitos de POO, ao separar classes de detecção, processamento, filtro, ações automatizadas.

- Implementação de Ações de Bot
    - A partir daqui surge a necessidade de concorrência, de modo que a aplicação continue rodando a captura de tela, mesmo quando aguarda as ações de Bot, do contrário a captura só atualizaria após o bot concluir a tarefa.
    - Portanto, inicia-se a aplicação dos conceitos de Threads e concorrência.
