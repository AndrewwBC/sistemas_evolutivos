# Roteiro — Epigenetic evolution of deep convolutional models
Hadjiivanov & Blair (UNSW), arXiv:2104.05411 (2021). Paper: `../2104.05411v1.pdf`

# Slide 1 - Título
O paper trata de **neuroevolução**: usar um algoritmo evolutivo para descobrir a
arquitetura de CNNs. "Epigenética" porque os filhos herdam os pesos que os pais
aprenderam em vida.

# Slide 2 - Roteiro
Contexto → método → experimentos → leitura crítica.

# Slide 3 - O paper em 30 segundos
Uma população de CNNs evolui ao longo de gerações. Em cada geração, toda rede é
treinada um pouco com backprop. Depois as redes sofrem mutações, cruzam entre si e
as piores são eliminadas. Os filhos herdam os pesos já treinados. São três
contribuições:
1. Camada convolucional em que **cada kernel tem seu próprio formato**, com uma
   mutação que redimensiona kernels individualmente.
2. Genoma e crossover do framework Cortex **estendidos para redes em camadas**.
3. **PyCortex**, a implementação open source sobre PyTorch.

# Slide 4 - Neuroevolução
NE é otimizar a estrutura e/ou os pesos de uma rede com evolução. Os trabalhos
clássicos (SANE, ESP, CMA-ES, NEAT, ~2000) usavam redes pequenas. NEAT
introduziu a **especiação**: redes parecidas competem só entre si, o que protege
inovações estruturais recentes. A tendência atual é a híbrida: a evolução busca
a estrutura (busca global) e o backprop ajusta os pesos (busca local). O paper
segue essa linha.

# Slide 5 - Kernel, stride e padding
O kernel (tamanho K) desliza sobre a entrada. O stride S diz quantas posições ele
pula a cada passo, e o padding P acrescenta zeros nas bordas para controlar o
tamanho da saída. Por convenção, todos os kernels de uma camada têm o mesmo
D×W×H, então o tamanho do kernel vira um atributo da camada. É justamente essa
convenção que o paper quebra.

# Slide 6 - MLP × CNN: a arquitetura completa
Na MLP tudo é camada densa. A imagem é achatada num vetor (28×28 → 784) e cada
neurônio da primeira camada tem um peso para cada pixel, então a noção de
vizinhança entre pixels se perde. Na CNN, as primeiras camadas são convolucionais:
cada kernel olha só uma janela local e é reaproveitado em toda a imagem, gerando
um mapa de resposta por kernel. No final, os mapas são achatados e entram numa
MLP comum (camadas FC), que classifica. Então **CNN = extrator de features +
MLP**. No paper não há pooling, só conv e FC, e a evolução mexe nas duas partes.

# Slide 7 - O kernel é um neurônio que desliza
O kernel equivale ao vetor de pesos de um neurônio da MLP. A diferença é que
ele não vê a entrada inteira: em cada posição, faz a soma ponderada
janela × pesos, soma o bias e passa pela ativação. Isso dá **um valor** do mapa
de resposta. Durante o forward, os pesos são **fixos** e iguais em todas as
posições (compartilhamento de pesos); só o backprop os altera, entre um lote e
outro. A dimensão do kernel (W×H×D) é o formato da sua matriz de pesos, e D é
sempre o número de canais da entrada. No paper, **nó = kernel**: adicionar um
kernel numa camada conv é como adicionar um neurônio numa camada oculta.

# Slide 8 - Cortex: genoma, genótipo, fenótipo
Cortex é o framework anterior dos mesmos autores. Ele tem três níveis:
- **Genoma**: o esqueleto de nós ordenados. Ele define a espécie.
- **Genótipo**: genoma + conexões, sem pesos. É o nível usado no crossover.
- **Fenótipo**: a rede real, com pesos.

A especiação usa o genoma: redes com a mesma quantidade de nós (e, aqui, de
camadas de cada tipo) formam uma espécie. A evolução é **epigenética/lamarckiana**
porque os pesos treinados passam aos filhos sem alteração, em vez de serem
reinicializados a cada geração.

# Slide 9 - Crossover em camadas
A extensão para CNNs trata cada **camada como um cromossomo** e cada **nó como
um gene**. Numa camada conv, o nó é um kernel, e ele vai junto com todas as
suas conexões de entrada e pesos. Se os pais são da mesma espécie, as camadas
batem em número e tamanho, então o filho herda kernels inteiros e é sempre uma
rede válida. Não é preciso criar nem podar conexões. A escolha de qual pai
fornece cada gene é proporcional ao fitness relativo. Sem especiação, a
similaridade s = O/(Ni+Nj−O) (a sobreposição de nós por camada) decide quem
cruza, e o que sobra do pai maior é herdado com probabilidade proporcional ao
fitness dele.

# Slide 10 - Kernels de formatos diferentes
Esta é a ideia nova. O formato (W×H) passa a ser propriedade **de cada kernel**,
e uma mesma camada pode ter 3×3, 1×7, 5×5, 7×1… Como W e H são sempre ímpares,
todos os kernels têm um elemento central. Eles são alinhados por esse centro e
empilhados num único tensor antes da convolução. Bibliotecas como o PyTorch não
suportam isso nativamente, daí o PyCortex. A inspiração é o Inception
(GoogLeNet), que já combina 1×1, 3×3 e 5×5.

# Slide 11 - Por que ajudaria
O argumento dos autores tem três partes:
- Kernels longos e finos funcionam como detectores de borda nítida, e um par
  ortogonal detecta cruzamentos.
- Subtrair um 5×5 de um 7×7 concêntrico gera um detector de contorno.
- Kernels grandes dão contexto aos detalhes captados pelos pequenos já na camada
  seguinte.

Ponto importante: **isso é hipótese**. O paper não faz ablação nem analisa os
kernels evoluídos (fica para trabalho futuro).

# Slide 12 - Mutações
- Kernel: cresce/encolhe W ou H em 2 (3×5 → 5×5 ou 3×7). Ele continua ímpar e o
  centro é preservado. Mínimo 1×1, máximo metade da entrada.
- Stride: ±1, raro, porque muda o tamanho de todas as camadas acima.
- Padding: fixo em ⌊maior kernel/2⌋, para que a saída tenha o tamanho da entrada
  e mutar um kernel não se propague como uma mutação de stride.
- Também é possível adicionar/remover nós e camadas (conv e FC).
- A probabilidade de cada tipo de mutação é inversamente proporcional a quantas
  conexões ela afeta (eqs. 3–6). O formato inicial é sorteado com p ∝ exp(−W·H),
  então as redes começam com kernels mínimos e crescem.

# Slide 13 - Uma geração
1. **Treino e avaliação**: backprop com Adadelta (sem precisar ajustar a taxa de
   aprendizado). O fitness é a acurácia no teste.
2. **Calibração**: fitness relativo = logística do z-score dentro da espécie. Fica
   em (0,1) e serve de probabilidade.
3. **Evolução**: mutação + crossover, com pais sorteados de forma proporcional ao
   fitness relativo.
4. **Culling**: se a população passa do limite, remove redes com probabilidade
   ∝ idade/(fitness·complexidade). Filhos novos e o campeão de cada espécie sempre
   sobrevivem.

# Slide 14 - Configuração
4 datasets de 10 classes (MNIST, Fashion-MNIST, SVHN, CIFAR-10), 10 execuções ×
100 gerações, com e sem especiação. Detalhe crucial: **cada rede treina em 10%
aleatórios dos dados por época**, então nenhuma rede vê tudo. Os filhos são
avaliados **antes** de qualquer treino. É isso que mede se o crossover transfere
conhecimento. A população vai de 64 a 111 redes (111 = núcleos disponíveis no
cluster), sem pooling, com batch 128.

# Slide 15 - Resultados (médias de 10 execuções, Tabela I)
- Melhor rede: com e sem especiação dá praticamente empate (MNIST ~98%, SVHN
  ~80%, Fashion ~88%, CIFAR-10 ~52%).
- Filhos antes do backprop: com especiação são muito melhores (MNIST 95,6% vs
  72,5%; SVHN 66,5% vs 44,4%; Fashion 82,0% vs 64,9%; CIFAR 42,7% vs 32,4%).

A especiação alinha os genes no crossover, e por isso os filhos nascem
funcionais. Sem ela, é preciso acrescentar/remover nós e o filho nasce pior.

# Slide 16 - Leitura crítica
**O achado:** como nenhuma rede viu o dataset todo, filhos com ~96% no MNIST
sem treino só podem vir de features aprendidas pelos pais e transferidas no
crossover. E o fitness dos filhos cresce ao longo das gerações.

**Limitações:**
- As redes ficam pequenas (~10⁵ parâmetros). Com especiação, o limite de 16
  espécies fez muitas mutações estruturais falharem e o tamanho estagnou, o que
  explica CIFAR-10 em ~55%.
- A ideia de kernels heterogêneos não foi isolada (sem ablação).
- O fitness é a acurácia **no conjunto de teste**, e a seleção usa esse número.
  Na prática o teste vira validação, então os números ficam otimistas. (Esta
  observação é minha, não do paper.)
- Só 10 execuções e nenhum teste de significância. Os próprios autores admitem.

# Slide 17 - Para aprofundar
Paper no arXiv, código PyCortex no GitLab, NEAT (especiação) e Inception
(kernels de vários tamanhos).
