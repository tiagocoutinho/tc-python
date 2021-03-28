#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <limits.h>
#include <math.h>
#include <time.h>

#define MIN(a,b) (((a)<(b))?(a):(b))
#define MAX(a,b) (((a)>(b))?(a):(b))

typedef struct shape_struct {
  int32_t x;
  int32_t y;
} Shape;

typedef int32_t Data;

typedef struct frame_struct {
  Shape shape;
  Data *data;
} Frame;

typedef struct stats_struct {
  Shape shape;
  int64_t min;
  int64_t max;
  int64_t sum;
  double std;
  double mean;
  int64_t *projection_x;
  int64_t *projection_y;
} Stats;


Stats *stats_new(Frame *frame) {
  int32_t sx = frame->shape.x, sy = frame->shape.y;
  int32_t size = sx * sy;
  Stats *stats = (Stats *)malloc(sizeof(Stats));
  stats->min = LONG_MAX;
  stats->max = LONG_MIN;
  stats->sum = 0;
  stats->shape = frame->shape;
  stats->projection_x = (int64_t*)malloc(sizeof(int64_t) * sx);
  stats->projection_y = (int64_t*)malloc(sizeof(int64_t) * sy);
  for(int32_t x = 0; x < sx; x++) {
    for(int32_t y = 0; y < sy; y++) {
      Data value = frame->data[x * sy + y];
      stats->min = MIN(stats->min, value);
      stats->max = MAX(stats->max, value);
      stats->sum += value;
      stats->projection_x[x] += value;
      stats->projection_y[y] += value;
    }
  }
  double mean = stats->sum / size;
  stats->mean = mean;
  // A second loop just for STD. We could use a single pass version like
  // https://www.strchr.com/standard_deviation_in_one_pass but seems
  // imprecise for "big" numbers.
  double sum_sq = 0;
  for(int32_t x = 0; x < sx; x++) {
    for(int32_t y = 0; y < sy; y++) {
      sum_sq += pow(frame->data[x * sy + y] - mean, 2);
    }
  }
  stats->std = sqrt(sum_sq / size);
  return stats;
}

void stats_delete(Stats *stats) {
  free(stats->projection_x);
  free(stats->projection_y);
  free(stats);
}

Frame *frame_new(Shape shape) {
  Frame *frame = (Frame *)malloc(sizeof(Frame));
  frame->shape = shape;
  frame->data = (Data *)malloc(sizeof(Data) * shape.x * shape.y);
  return frame;
}

void frame_delete(Frame *frame) {
  free(frame->data);
  free(frame);
}

int main(int argc, char* argv[]) {
  Shape shape = {x: 1920, y:1080};
  int32_t size = shape.x * shape.y;
  Frame *frame = frame_new(shape);
  for(int32_t i = 0; i < size; i++) {
    frame->data[i] = i;
  }

  // real stats
  Stats *stats = stats_new(frame);
  printf("min=%ld max=%ld sum=%ld mean=%f std=%f\n",
	 stats->min, stats->max, stats->sum, stats->mean, stats->std);
  stats_delete(stats);

  // sampling
  struct timespec start, stop;
  double elapsed_sum = 0;
  int N = 100;
  for(int i = 0; i < N; i++) {
    clock_gettime(CLOCK_MONOTONIC, &start);
    Stats *s = stats_new(frame);
    clock_gettime(CLOCK_MONOTONIC, &stop);
    elapsed_sum += (stop.tv_sec + stop.tv_nsec * 1E-9) - (start.tv_sec + start.tv_nsec * 1E-9);
    stats_delete(s);
  }
  double elapsed_avg_ms = elapsed_sum / N * 1000;
  printf("avg time = %f ms per loop\n", elapsed_avg_ms);

  frame_delete(frame);
  return 0;
}
