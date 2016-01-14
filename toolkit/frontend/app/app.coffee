
App = init: ->
  console.log 'App initialized!'

  elementary = new (terra.Terrarium)(150, 150)

  terra.registerCA
    type: 'elementary'
    alive: false
    ruleset: [1, 0, 0, 1, 0, 0, 1, 0].reverse()
    colorFn: ->
      if @alive then @color + ',1' else '0,0,0,0'
    process: (neighbors, x, y) ->
      if @age == y
        index = neighbors.filter((neighbor) ->
          neighbor.coords.y == y - 1
        ).map((neighbor) ->
          if neighbor.creature.alive then 1 else 0
        )
        index = parseInt(index.join(''), 2)
        @alive = if isNaN(index) then !x else @ruleset[index]
      true
  elementary.grid = elementary.makeGrid('elementary')
  elementary.animate()

  models:
    gene:
      type: 'gene'
      symbol: undefined
      age: 0
      actionRadius: 1
      color: [30, 0, 30]
      colorFn: ->
        #: Returns the creature's color at each step.
        #: The color is determined on the basis of genes.
        @color
      isDead: ->
        #: Determines if the gene is degraded and should be removed.
        no
      move: (neighbors) ->
      process: (neighbors, x, y) ->
      reproduce: (neighbors) ->
      wait:->

    mirna:
      type: 'mirna'
      symbol: undefined
      age: 0
      targets: []

    mirna_gene_complex:
      type: 'mirna_gene_complex'
      gene_ref: undefined
      mirna_ref: undefined
      age: 0
      dGbinding: 0

    rrna:
      type: 'rRNA'

    rrna_gene_complex:
      type: 'rrna_gene_complex'

    protein:
      type: 'protein'

    source:
      type: 'source'

    sink:
      type: 'sink'

module.exports = App
