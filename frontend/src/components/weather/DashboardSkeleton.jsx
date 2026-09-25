import { Skeleton } from '@/components/ui/Skeleton';

const TILE_COUNT = 8;

export function DashboardSkeleton() {
  return (
    <>
      <section className="glass-surface p-4 p-md-5 mb-4">
        <Skeleton height={24} width="40%" />
        <div className="mt-3">
          <Skeleton height={16} width="25%" />
        </div>
        <div className="mt-4">
          <Skeleton height={72} width="45%" radius="var(--radius-md)" />
        </div>
      </section>

      <div className="row g-3">
        {Array.from({ length: TILE_COUNT }, (_, index) => (
          <div className="col-6 col-md-4 col-xl-3" key={index}>
            <div className="glass-surface p-3">
              <Skeleton height={14} width="60%" />
              <div className="mt-3">
                <Skeleton height={28} width="45%" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
