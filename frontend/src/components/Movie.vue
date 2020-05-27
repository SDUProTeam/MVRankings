<template>
	<dd>
			<div class="movie-item film-channel">
				<a :href="data.url" target="_blank" data-act="movie-click" :data-val="id">
					<div class="movie-poster">
						<img :src="data.cover" :alt="data.name" />
					</div>
				</a>
				<div class="movie-ver"></div>
				<div class="movie-item-hover">
					<a :href="data.url" target="_blank" data-act="movie-click" :data-val="id">
						<img class="movie-hover-img" :src="data.cover" :alt="data.name" />
						<div class="movie-hover-info">
							<div class="movie-hover-title" :title="data.name" >
								<span class="name ">{{data.name}}</span>
								<span class="score channel-detail-orange">
										<i class="integer">{{data.integer}}</i>
										<i class="fraction">{{data.fraction}}</i>
								</span>
							</div>
							<div class="movie-hover-title" :title="data.name" >
								<span class="hover-tag">类型:</span>
								{{data.type}}
							</div>
							<div class="movie-hover-title" :title="data.name" >
								<span class="hover-tag">导演:</span>
								{{data.directors}}
							</div>
							<div class="movie-hover-title" :title="data.name" >
								<span class="hover-tag">主演:</span>
								{{data.casts}}
							</div>
							<div class="movie-hover-title movie-hover-brief" :title="data.name" >
								<span class="hover-tag">上映时间:</span>
								{{data.time}}
							</div>
							<div class="movie-hover-title movie-hover-brief" :title="data.name" >
								<span class="hover-tag">来源:</span>
								{{data.source}}
							</div>
						</div>
					</a>
				</div>
			</div>
			
			<div class="channel-detail movie-item-title" :title="data.name">
				<el-link :href="data.url" target="_blank" data-act="movies-click" :data-val="id">{{data.name}}</el-link>
			</div>
			<div class="channel-detail channel-detail-orange">
				<i class="integer">{{data.integer}}</i>
				<i class="fraction">{{data.fraction}}</i>
				<span class="no-rate" v-if="!data.integer">暂无评分</span>
			</div>
	</dd>
</template>

<script>
export default {
  props: ["data"], 
  methods: {
  }
};
</script>

<style>

 dd {
	margin: 10px 40px 10px 40px;
	display: inline-block;
	vertical-align: top;
	position: relative
}

.movie-item {
	position: relative;
	border: 1px solid #efefef;
	margin: -1px
}

.movie-item:hover {
	-moz-box-shadow: 0 0 8px #fff,0 5px 13px rgba(0,0,0,.07);
	-webkit-box-shadow: 0 0 8px #fff,0 5px 13px rgba(0,0,0,.07);
	box-shadow: 0 0 8px #fff,0 5px 13px rgba(0,0,0,.07)
}

.film-channel:hover .movie-item-hover {
	display: block
}

.movie-item-hover {
	display: none;
	position: absolute;
	width: 218px;
	height: 350px;
	z-index: 10;
	top: -40px;
	left: -29px;
	overflow: hidden;
	background: #fff;
	-moz-box-shadow: 0 0 16px #fff,0 0 6px rgba(0,0,0,.2);
	-webkit-box-shadow: 0 0 16px #fff,0 0 6px rgba(0,0,0,.2);
	box-shadow: 0 0 16px #fff,0 0 6px rgba(0,0,0,.2)
}

.movie-item-hover .name {
	float: left;
	width: 140px;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
	text-align: start;
}

.movie-item-hover .noscore {
	width: 100%
}

.movie-item-hover .score {
	float: right;
	margin-right: 5px
}

.movie-hover-img {
	width: 218px;
	height: 300px;
	vertical-align: middle;
	/* position: absolute; */
	z-index: 10
}

.movie-hover-info {
	padding: 16px;
	height: 150px;
	box-sizing: border-box;
	position: absolute;
	z-index: 11;
	top: 150px;
	background: #fff;
	width: 218px
}

.movie-hover-title {
	font-size: 16px;
	line-height: 16px;
	color: #999;
	margin-top: 12px;
	width: 100%;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
	text-align: start;
}

.movie-hover-title:first-child {
	margin-top: 6px;
	font-size: 20px;
	color: #333;
	line-height: 20px;
	text-align: start;
}

.movie-hover-title:last-child {
	white-space: normal;
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
	line-height: 20px;
	margin-top: 10px
}

.hover-tag {
	color: #333
}

.movie-poster {
	background-color: #fcfcfc;
	width: 160px;
	height: 220px;
	overflow: hidden;
	position: relative
}

.movie-poster-long {
	width: 350px;
	height: 220px
}

.movie-poster a {
	display: block
}

.movie-poster .poster-default {
	top: 50%;
	left: 50%;
	width: 68px;
	height: 62px;
	margin-top: -31px;
	margin-left: -34px
}

.movie-poster img {
	width: 100%;
	position: absolute;
	top: 0;
	left: 0
}

.movie-poster .movie-poster-img[src] {
	visibility: visible
}

.movie-poster .movie-poster-img[data-src] {
	visibility: hidden
}

.movie-poster .movie-overlay {
	width: 100%;
	height: 100%;
	position: absolute;
	top: 0;
	left: 0
}

.movie-overlay .movie-info {
	color: #fff;
	position: absolute;
	bottom: 7px;
	width: 100%
}

.movie-ver {
	position: absolute;
	top: 4px;
	left: -2px;
	font-size: 12px;
	color: #fff
}

.movie-score {
	color: #ffb400;
	float: right;
	margin-right: 10px
}

.movie-score .integer {
	font-size: 18px
}

.movie-score .fraction {
	font-size: 14px
}

.channel-detail {
	width: 160px;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
	text-align: center;
	font-size: 16px;
	color: #333;
	margin-top: 10px
}

.channel-detail a {
	color: #333
}

.channel-detail-orange,.channel-detail-prescore {
	color: #ffb400
}

.channel-detail-orange .integer {
	font-size: 24px
}

.channel-detail-orange .fraction {
	font-size: 22px
}

.channel-detail-orange .no-rate {
	font-size: 18px
}

</style>


