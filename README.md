# ProgramacaoGenetica

## Relatório de Alterações

1. Novos Operadores
- sin, cos: permitem navegação angular mais refinada
- media: suaviza a transição entre valores
- prioridade: executa uma ação preferencial se seu valor for alto
- if_then_else: condicional completo com condição, então, senão
- if_maior e if_menor: para decisões mais complexas
- raiz_quadrada: para normalização de distâncias
- potencia: para cálculos exponenciais (com limite de 3 para evitar overflow)

2. Valores das Constantes
- Mantido o range para random.uniform(-10, 10) para permitir comportamentos mais extremos

3. Parâmetros do Algoritmo Genético
- Aumentado o tamanho da população para 300 indivíduos (era 200)
- Reduzida a profundidade da árvore para 5 níveis (era 6)

4. Probabilidade de Mutação
- Implementada mutação adaptativa que começa em 0.2 e diminui linearmente com as gerações
- Fórmula: 0.2 * (1 - geracao/n_geracoes)

5. Função de Fitness
- Aumentado o peso dos recursos coletados para 500 (era 300)
- Aumentado o bônus por manter energia para 0.5 (era 0.3)
- Aumentada a penalidade por ficar parado para 0.8 (era 0.5)
- Reduzido o peso da distância percorrida para 0.1 (era 0.2)
- Aumentada a penalidade de colisão para 50 (era 30)
- Aumentado o bônus por atingir a meta para 10000 (era 5000)
- Adicionados novos bônus:
  * Bônus por atingir a meta com energia: energia * 2
  * Bônus por atingir a meta com poucas colisões: (10 - min(colisoes, 10)) * 100
  * Bônus por coletar todos os recursos: 2000

6. Método de Seleção
- Aumentado o tamanho do torneio para 7 (era 5)
- Aumentado o elitismo para 20% (era 10%)
- Implementada seleção probabilística:
  * 80% de chance de selecionar o melhor do torneio
  * 20% de chance de selecionar aleatoriamente para manter diversidade

7. Múltiplas Populações Paralelas
- Implementado sistema de 5 populações paralelas
- Adicionada migração de indivíduos entre populações a cada 10 gerações
- Melhor indivíduo de cada população migra para a próxima população

8. Parâmetros de Treinamento Otimizados
- Ajustado tamanho da população para 500 indivíduos (era 300)
- Ajustado número de gerações para 50 (era 10)
- Implementada profundidade variável nas árvores:
  * Profundidade mínima: 3
  * Profundidade máxima: 6

9. Seleção por Torneio Dinâmico
- Tamanho do torneio varia de 3 a 10 baseado na geração atual
- Fórmula: max(3, min(10, int(5 + (geracao / n_geracoes) * 5)))
- Mantém pressão seletiva mais alta no início e mais baixa no final

10. Sistema de Elitismo Global
- Mantém registro do melhor indivíduo global entre todas as populações
- Permite que o melhor indivíduo seja preservado independente da população

---------------------------------------
## Correção de Bug 
11. O Problema de Overflow:
- O erro "overflow encountered" ocorre quando um cálculo matemático resulta em um número que é maior do que o tipo de dado pode representar
- No nosso caso, estava acontecendo principalmente nos cálculos de distância usando np.sqrt(dx*dx + dy*dy)
- Quando multiplicamos números grandes (dxdx e dydy), o resultado pode exceder o limite do tipo de dado

12. Por que o problema acontecia:
- Quando o robô estava muito longe de um recurso ou da meta, as diferenças de coordenadas (dx e dy) podiam ser muito grandes
- Ao elevar esses números ao quadrado (dxdx e dydy), o resultado podia ser tão grande que causava overflow
- Por exemplo, se dx = 10000, então dxdx = 100000000, que pode causar problemas em alguns tipos de dados

13. A solução implementada:
- Substituímos o cálculo np.sqrt(dx*dx + dy*dy) por np.hypot(dx, dy)
- O np.hypot é uma função especializada que:
    - Calcula a hipotenusa de forma mais segura
    - Evita problemas de overflow mesmo com números grandes
    - É mais precisa numericamente
- Convertemos explicitamente os números para float para garantir que tenhamos precisão suficiente

14. Por que a solução funciona:
- O np.hypot usa um algoritmo mais sofisticado que:
    - Evita multiplicações diretas de números grandes
    - Normaliza os números antes de fazer os cálculos
    - Lida melhor com casos extremos
- A conversão para float garante que temos 64 bits de precisão

15. Benefícios das mudanças:
- Eliminação dos avisos de overflow
- Cálculos mais precisos
- Código mais robusto
- Melhor comportamento do robô em situações extremas